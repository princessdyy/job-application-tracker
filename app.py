import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from database import query_db, execute_db, test_connection, get_db_diagnostics

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fiu-job-application-tracker-secret-2026')


# -----------------------------------------------------------------------------
# Jinja Custom Filters & Context Processors
# -----------------------------------------------------------------------------
@app.template_filter('from_json')
def from_json_filter(val):
    if not val:
        return []
    if isinstance(val, (list, dict)):
        return val
    try:
        return json.loads(val)
    except (ValueError, TypeError):
        return []


@app.template_filter('currency')
def currency_filter(val):
    if val is None or val == '':
        return 'N/A'
    try:
        return f"${int(val):,}"
    except (ValueError, TypeError):
        return str(val)


@app.context_processor
def inject_global_data():
    """Provides database status and dynamic day name to all templates."""
    is_connected, msg = test_connection()
    today_day_plural = datetime.now().strftime('%A') + 's'  # e.g. "Mondays", "Sundays"
    diag = get_db_diagnostics()
    return dict(
        db_connected=is_connected, 
        db_status_msg=msg,
        db_diag=diag,
        today_day_name=today_day_plural
    )


# -----------------------------------------------------------------------------
# Dashboard Route
# -----------------------------------------------------------------------------
@app.route('/')
def dashboard():
    try:
        # Aggregate statistics
        app_counts = query_db("""
            SELECT 
                COUNT(*) AS total_apps,
                SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END) AS applied_count,
                SUM(CASE WHEN status = 'Screening' THEN 1 ELSE 0 END) AS screening_count,
                SUM(CASE WHEN status = 'Interview' THEN 1 ELSE 0 END) AS interview_count,
                SUM(CASE WHEN status = 'Offer' THEN 1 ELSE 0 END) AS offer_count,
                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) AS rejected_count,
                SUM(CASE WHEN status = 'Withdrawn' THEN 1 ELSE 0 END) AS withdrawn_count
            FROM applications
        """, one=True) or {}

        company_count = query_db("SELECT COUNT(*) AS total FROM companies", one=True)['total']
        job_count = query_db("SELECT COUNT(*) AS total FROM jobs", one=True)['total']
        contact_count = query_db("SELECT COUNT(*) AS total FROM contacts", one=True)['total']

        # Recent applications with company and job titles
        recent_apps = query_db("""
            SELECT 
                a.application_id,
                a.application_date,
                a.status,
                a.resume_version,
                a.cover_letter_sent,
                a.interview_data,
                j.job_title,
                j.job_type,
                c.company_name,
                c.city,
                c.state
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC, a.application_id DESC
            LIMIT 5
        """)

        # Extract scheduled/past interviews from JSON field across applications
        upcoming_interviews = []
        all_apps = query_db("""
            SELECT a.application_id, a.interview_data, j.job_title, c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            WHERE a.interview_data IS NOT NULL
        """)

        for row in all_apps:
            rounds = from_json_filter(row.get('interview_data'))
            if isinstance(rounds, list):
                for r in rounds:
                    if isinstance(r, dict) and r.get('round'):
                        upcoming_interviews.append({
                            'application_id': row['application_id'],
                            'company_name': row['company_name'],
                            'job_title': row['job_title'],
                            'round': r.get('round'),
                            'date': r.get('date', 'TBD'),
                            'notes': r.get('notes', '')
                        })

        return render_template(
            'dashboard.html',
            stats=app_counts,
            company_count=company_count,
            job_count=job_count,
            contact_count=contact_count,
            recent_apps=recent_apps,
            interviews=upcoming_interviews[:6]
        )
    except Exception as e:
        flash(f"Database error loading dashboard: {str(e)}", "danger")
        return render_template('dashboard.html', stats={}, company_count=0, job_count=0, contact_count=0, recent_apps=[], interviews=[])


# -----------------------------------------------------------------------------
# COMPANIES CRUD
# -----------------------------------------------------------------------------
@app.route('/companies')
def list_companies():
    try:
        search = request.args.get('search', '').strip()
        if search:
            query = """
                SELECT c.*, 
                       COUNT(DISTINCT j.job_id) AS job_count,
                       COUNT(DISTINCT ct.contact_id) AS contact_count
                FROM companies c
                LEFT JOIN jobs j ON c.company_id = j.company_id
                LEFT JOIN contacts ct ON c.company_id = ct.company_id
                WHERE c.company_name LIKE %s OR c.industry LIKE %s OR c.city LIKE %s
                GROUP BY c.company_id
                ORDER BY c.company_name ASC
            """
            search_param = f"%{search}%"
            companies = query_db(query, (search_param, search_param, search_param))
        else:
            query = """
                SELECT c.*, 
                       COUNT(DISTINCT j.job_id) AS job_count,
                       COUNT(DISTINCT ct.contact_id) AS contact_count
                FROM companies c
                LEFT JOIN jobs j ON c.company_id = j.company_id
                LEFT JOIN contacts ct ON c.company_id = ct.company_id
                GROUP BY c.company_id
                ORDER BY c.company_name ASC
            """
            companies = query_db(query)
        return render_template('companies.html', companies=companies, search_term=search)
    except Exception as e:
        flash(f"Error fetching companies: {str(e)}", "danger")
        return render_template('companies.html', companies=[], search_term='')


@app.route('/companies/add', methods=['POST'])
def add_company():
    company_name = request.form.get('company_name', '').strip()
    industry = request.form.get('industry', '').strip()
    website = request.form.get('website', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    notes = request.form.get('notes', '').strip()

    if not company_name:
        flash("Company name is required.", "warning")
        return redirect(url_for('list_companies'))

    try:
        execute_db("""
            INSERT INTO companies (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (company_name, industry or None, website or None, city or None, state or None, notes or None))
        flash(f"Company '{company_name}' successfully added!", "success")
    except Exception as e:
        flash(f"Error adding company: {str(e)}", "danger")
    return redirect(url_for('list_companies'))


@app.route('/companies/edit/<int:company_id>', methods=['POST'])
def edit_company(company_id):
    company_name = request.form.get('company_name', '').strip()
    industry = request.form.get('industry', '').strip()
    website = request.form.get('website', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    notes = request.form.get('notes', '').strip()

    if not company_name:
        flash("Company name is required.", "warning")
        return redirect(url_for('list_companies'))

    try:
        execute_db("""
            UPDATE companies
            SET company_name = %s, industry = %s, website = %s, city = %s, state = %s, notes = %s
            WHERE company_id = %s
        """, (company_name, industry or None, website or None, city or None, state or None, notes or None, company_id))
        flash(f"Company '{company_name}' updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating company: {str(e)}", "danger")
    return redirect(url_for('list_companies'))


@app.route('/companies/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    try:
        execute_db("DELETE FROM companies WHERE company_id = %s", (company_id,))
        flash("Company and associated jobs/contacts deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting company: {str(e)}", "danger")
    return redirect(url_for('list_companies'))


# -----------------------------------------------------------------------------
# JOBS CRUD
# -----------------------------------------------------------------------------
@app.route('/jobs')
def list_jobs():
    try:
        company_filter = request.args.get('company_id', '')
        keyword = request.args.get('keyword', '').strip()
        location = request.args.get('location', '').strip()
        companies = query_db("SELECT company_id, company_name FROM companies ORDER BY company_name")

        conditions = []
        params = []

        if company_filter and company_filter.isdigit():
            conditions.append("j.company_id = %s")
            params.append(int(company_filter))

        if keyword:
            conditions.append("(j.job_title LIKE %s OR j.requirements LIKE %s OR c.company_name LIKE %s)")
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])

        if location:
            conditions.append("(c.city LIKE %s OR c.state LIKE %s)")
            loc = f"%{location}%"
            params.extend([loc, loc])

        where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        query = f"""
            SELECT j.*, c.company_name, c.city, c.state,
                   (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.job_id) AS app_count
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            {where_clause}
            ORDER BY j.date_posted DESC, j.job_id DESC
        """
        jobs = query_db(query, tuple(params))

        return render_template('jobs.html', jobs=jobs, companies=companies, selected_company=company_filter)
    except Exception as e:
        flash(f"Error fetching jobs: {str(e)}", "danger")
        return render_template('jobs.html', jobs=[], companies=[], selected_company='')


@app.route('/jobs/add', methods=['POST'])
def add_job():
    company_id = request.form.get('company_id')
    job_title = request.form.get('job_title', '').strip()
    job_type = request.form.get('job_type', 'Full-time')
    salary_min = request.form.get('salary_min') or None
    salary_max = request.form.get('salary_max') or None
    job_url = request.form.get('job_url', '').strip() or None
    date_posted = request.form.get('date_posted') or datetime.now().strftime('%Y-%m-%d')
    requirements_raw = request.form.get('requirements', '').strip()

    if not company_id or not job_title:
        flash("Company and Job Title are required.", "warning")
        return redirect(url_for('list_jobs'))

    try:
        if requirements_raw.startswith('[') and requirements_raw.endswith(']'):
            parsed_reqs = json.loads(requirements_raw)
        else:
            parsed_reqs = [req.strip() for req in requirements_raw.split(',') if req.strip()]
        req_json = json.dumps(parsed_reqs)
    except Exception:
        req_json = json.dumps([r.strip() for r in requirements_raw.split(',') if r.strip()])

    try:
        execute_db("""
            INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, req_json))
        flash(f"Job posting '{job_title}' added successfully!", "success")
    except Exception as e:
        flash(f"Error adding job: {str(e)}", "danger")
    return redirect(url_for('list_jobs'))


@app.route('/jobs/edit/<int:job_id>', methods=['POST'])
def edit_job(job_id):
    company_id = request.form.get('company_id')
    job_title = request.form.get('job_title', '').strip()
    job_type = request.form.get('job_type', 'Full-time')
    salary_min = request.form.get('salary_min') or None
    salary_max = request.form.get('salary_max') or None
    job_url = request.form.get('job_url', '').strip() or None
    date_posted = request.form.get('date_posted') or None
    requirements_raw = request.form.get('requirements', '').strip()

    if not company_id or not job_title:
        flash("Company and Job Title are required.", "warning")
        return redirect(url_for('list_jobs'))

    try:
        if requirements_raw.startswith('[') and requirements_raw.endswith(']'):
            parsed_reqs = json.loads(requirements_raw)
        else:
            parsed_reqs = [req.strip() for req in requirements_raw.split(',') if req.strip()]
        req_json = json.dumps(parsed_reqs)
    except Exception:
        req_json = json.dumps([r.strip() for r in requirements_raw.split(',') if r.strip()])

    try:
        execute_db("""
            UPDATE jobs
            SET company_id = %s, job_title = %s, job_type = %s, salary_min = %s, salary_max = %s, 
                job_url = %s, date_posted = %s, requirements = %s
            WHERE job_id = %s
        """, (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, req_json, job_id))
        flash(f"Job '{job_title}' updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating job: {str(e)}", "danger")
    return redirect(url_for('list_jobs'))


@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        execute_db("DELETE FROM jobs WHERE job_id = %s", (job_id,))
        flash("Job posting deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting job: {str(e)}", "danger")
    return redirect(url_for('list_jobs'))


# -----------------------------------------------------------------------------
# APPLICATIONS CRUD
# -----------------------------------------------------------------------------
@app.route('/applications')
def list_applications():
    try:
        status_filter = request.args.get('status', '').strip()
        jobs = query_db("""
            SELECT j.job_id, j.job_title, c.company_name 
            FROM jobs j 
            JOIN companies c ON j.company_id = c.company_id 
            ORDER BY c.company_name, j.job_title
        """)

        if status_filter:
            query = """
                SELECT a.*, j.job_title, j.job_type, c.company_name, c.company_id
                FROM applications a
                JOIN jobs j ON a.job_id = j.job_id
                JOIN companies c ON j.company_id = c.company_id
                WHERE a.status = %s
                ORDER BY a.application_date DESC, a.application_id DESC
            """
            applications = query_db(query, (status_filter,))
        else:
            query = """
                SELECT a.*, j.job_title, j.job_type, c.company_name, c.company_id
                FROM applications a
                JOIN jobs j ON a.job_id = j.job_id
                JOIN companies c ON j.company_id = c.company_id
                ORDER BY a.application_date DESC, a.application_id DESC
            """
            applications = query_db(query)

        return render_template('applications.html', applications=applications, jobs=jobs, selected_status=status_filter)
    except Exception as e:
        flash(f"Error fetching applications: {str(e)}", "danger")
        return render_template('applications.html', applications=[], jobs=[], selected_status='')


@app.route('/applications/add', methods=['POST'])
def add_application():
    job_id = request.form.get('job_id')
    application_date = request.form.get('application_date') or datetime.now().strftime('%Y-%m-%d')
    status = request.form.get('status', 'Applied')
    resume_version = request.form.get('resume_version', '').strip() or None
    cover_letter_sent = 1 if request.form.get('cover_letter_sent') == '1' else 0
    interview_notes = request.form.get('interview_notes', '').strip()
    interview_round = request.form.get('interview_round', '').strip()
    interview_date = request.form.get('interview_date', '').strip()

    if not job_id:
        flash("Job selection is required.", "warning")
        return redirect(url_for('list_applications'))

    interview_list = []
    if interview_round or interview_notes:
        interview_list.append({
            "round": interview_round or "Initial Contact",
            "date": interview_date or application_date,
            "notes": interview_notes
        })
    interview_json = json.dumps(interview_list)

    try:
        execute_db("""
            INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (job_id, application_date, status, resume_version, cover_letter_sent, interview_json))
        flash("Application tracked successfully!", "success")
    except Exception as e:
        flash(f"Error creating application: {str(e)}", "danger")
    return redirect(url_for('list_applications'))


@app.route('/applications/edit/<int:app_id>', methods=['POST'])
def edit_application(app_id):
    job_id = request.form.get('job_id')
    application_date = request.form.get('application_date')
    status = request.form.get('status', 'Applied')
    resume_version = request.form.get('resume_version', '').strip() or None
    cover_letter_sent = 1 if request.form.get('cover_letter_sent') == '1' else 0
    raw_interview_data = request.form.get('interview_data', '').strip()

    try:
        if raw_interview_data:
            json.loads(raw_interview_data)
            clean_interview_json = raw_interview_data
        else:
            clean_interview_json = '[]'
    except Exception:
        clean_interview_json = json.dumps([{"round": "Notes", "date": application_date, "notes": raw_interview_data}])

    try:
        execute_db("""
            UPDATE applications
            SET job_id = %s, application_date = %s, status = %s, resume_version = %s,
                cover_letter_sent = %s, interview_data = %s
            WHERE application_id = %s
        """, (job_id, application_date, status, resume_version, cover_letter_sent, clean_interview_json, app_id))
        flash("Application updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating application: {str(e)}", "danger")
    return redirect(url_for('list_applications'))


@app.route('/applications/delete/<int:app_id>', methods=['POST'])
def delete_application(app_id):
    try:
        execute_db("DELETE FROM applications WHERE application_id = %s", (app_id,))
        flash("Application record removed.", "info")
    except Exception as e:
        flash(f"Error deleting application: {str(e)}", "danger")
    return redirect(url_for('list_applications'))


# -----------------------------------------------------------------------------
# CONTACTS CRUD
# -----------------------------------------------------------------------------
@app.route('/contacts')
def list_contacts():
    try:
        company_filter = request.args.get('company_id', '')
        companies = query_db("SELECT company_id, company_name FROM companies ORDER BY company_name")

        if company_filter and company_filter.isdigit():
            query = """
                SELECT ct.*, c.company_name
                FROM contacts ct
                JOIN companies c ON ct.company_id = c.company_id
                WHERE ct.company_id = %s
                ORDER BY ct.contact_name ASC
            """
            contacts = query_db(query, (int(company_filter),))
        else:
            query = """
                SELECT ct.*, c.company_name
                FROM contacts ct
                JOIN companies c ON ct.company_id = c.company_id
                ORDER BY c.company_name ASC, ct.contact_name ASC
            """
            contacts = query_db(query)

        return render_template('contacts.html', contacts=contacts, companies=companies, selected_company=company_filter)
    except Exception as e:
        flash(f"Error fetching contacts: {str(e)}", "danger")
        return render_template('contacts.html', contacts=[], companies=[], selected_company='')


@app.route('/contacts/add', methods=['POST'])
def add_contact():
    company_id = request.form.get('company_id')
    contact_name = request.form.get('contact_name', '').strip()
    title = request.form.get('title', '').strip() or None
    email = request.form.get('email', '').strip() or None
    phone = request.form.get('phone', '').strip() or None
    linkedin_url = request.form.get('linkedin_url', '').strip() or None
    notes = request.form.get('notes', '').strip() or None

    if not company_id or not contact_name:
        flash("Company and Contact Name are required.", "warning")
        return redirect(url_for('list_contacts'))

    try:
        execute_db("""
            INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (company_id, contact_name, title, email, phone, linkedin_url, notes))
        flash(f"Contact '{contact_name}' saved successfully!", "success")
    except Exception as e:
        flash(f"Error adding contact: {str(e)}", "danger")
    return redirect(url_for('list_contacts'))


@app.route('/contacts/edit/<int:contact_id>', methods=['POST'])
def edit_contact(contact_id):
    company_id = request.form.get('company_id')
    contact_name = request.form.get('contact_name', '').strip()
    title = request.form.get('title', '').strip() or None
    email = request.form.get('email', '').strip() or None
    phone = request.form.get('phone', '').strip() or None
    linkedin_url = request.form.get('linkedin_url', '').strip() or None
    notes = request.form.get('notes', '').strip() or None

    if not company_id or not contact_name:
        flash("Company and Contact Name are required.", "warning")
        return redirect(url_for('list_contacts'))

    try:
        execute_db("""
            UPDATE contacts
            SET company_id = %s, contact_name = %s, title = %s, email = %s, phone = %s,
                linkedin_url = %s, notes = %s
            WHERE contact_id = %s
        """, (company_id, contact_name, title, email, phone, linkedin_url, notes, contact_id))
        flash(f"Contact '{contact_name}' updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating contact: {str(e)}", "danger")
    return redirect(url_for('list_contacts'))


@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    try:
        execute_db("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))
        flash("Contact deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting contact: {str(e)}", "danger")
    return redirect(url_for('list_contacts'))


# -----------------------------------------------------------------------------
# JOB MATCH FEATURE (Skills Matching Engine)
# -----------------------------------------------------------------------------
@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    user_skills_input = ""
    match_results = []
    has_searched = False

    if request.method == 'POST':
        user_skills_input = request.form.get('skills', '').strip()
        has_searched = True

    elif request.method == 'GET' and request.args.get('skills'):
        user_skills_input = request.args.get('skills', '').strip()
        has_searched = True

    if has_searched and user_skills_input:
        candidate_skills = [s.strip().lower() for s in user_skills_input.replace(';', ',').split(',') if s.strip()]
        candidate_skill_set = set(candidate_skills)

        try:
            jobs = query_db("""
                SELECT j.job_id, j.job_title, j.job_type, j.salary_min, j.salary_max, 
                       j.job_url, j.requirements, c.company_name, c.city, c.state
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id
            """)

            for job in jobs:
                reqs = from_json_filter(job.get('requirements'))
                if not isinstance(reqs, list):
                    reqs = []

                matched_skills = []
                missing_skills = []

                for req in reqs:
                    req_clean = str(req).strip()
                    if any(c_skill == req_clean.lower() or c_skill in req_clean.lower() for c_skill in candidate_skill_set):
                        matched_skills.append(req_clean)
                    else:
                        missing_skills.append(req_clean)

                total_reqs = len(reqs)
                matched_count = len(matched_skills)
                percentage = round((matched_count / total_reqs) * 100) if total_reqs > 0 else 0

                match_results.append({
                    'job_id': job['job_id'],
                    'job_title': job['job_title'],
                    'company_name': job['company_name'],
                    'city': job['city'],
                    'state': job['state'],
                    'job_type': job['job_type'],
                    'salary_min': job['salary_min'],
                    'salary_max': job['salary_max'],
                    'job_url': job['job_url'],
                    'total_skills': total_reqs,
                    'matched_count': matched_count,
                    'match_percentage': percentage,
                    'matched_skills': matched_skills,
                    'missing_skills': missing_skills
                })

            match_results.sort(key=lambda x: (x['match_percentage'], x['matched_count']), reverse=True)

        except Exception as e:
            flash(f"Error calculating job matches: {str(e)}", "danger")

    return render_template(
        'job_match.html',
        user_skills_input=user_skills_input,
        match_results=match_results,
        has_searched=has_searched
    )


# -----------------------------------------------------------------------------
# Main Application Entrypoint
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
