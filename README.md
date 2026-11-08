# Job Application Tracker

A full-stack web application designed to track and streamline the job search pipeline, manage recruiter relationships, monitor interview rounds, and calculate skill match percentages for open positions.

Built for the **Course Project: Job Application Tracker** using **MySQL**, **Python 3 with Flask**, and **HTML5/CSS3**.

- **GitHub Repository**: [https://github.com/princessdyy/job-application-tracker](https://github.com/princessdyy/job-application-tracker)

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Database Architecture](#database-architecture)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Installation & Setup](#installation--setup)
7. [Running the Application](#running-the-application)
8. [Features Walkthrough](#features-walkthrough)
9. [Video Recording Submission Checklist](#video-recording-submission-checklist)
10. [GenAI Documentation](#genai-documentation)

---

## Project Overview

The **Job Application Tracker** provides an intuitive, executive-grade dashboard and management system to track:
- **Companies**: Target employers, industry classifications, and locations.
- **Jobs**: Open positions, salary ranges, and **JSON** skill requirements.
- **Applications**: Full lifecycle tracking (`Applied`, `Screening`, `Interview`, `Offer`, `Rejected`, `Withdrawn`), resume versioning, and **JSON** interview timelines.
- **Contacts**: Recruiters, hiring managers, and networking leads.
- **Job Match Engine**: Calculates skill match percentages against stored job requirements and presents a ranked list with matched and missing skill breakdowns.

---

## Tech Stack

- **Backend**: Python 3.10+, Flask 2.3+, `mysql-connector-python`, `python-dotenv`
- **Database**: MySQL 8.0+ (InnoDB, UTF-8 unicode collation, native JSON support)
- **Frontend**: HTML5, Jinja2 templates, Custom CSS, Bootstrap 5.3, Bootstrap Icons
- **Version Control**: Git & GitHub

---

## Database Architecture

The relational schema consists of four interconnected tables:

```
+----------------+          1 : N          +---------------+          1 : N          +--------------------+
|   companies    | ----------------------> |     jobs      | ----------------------> |    applications    |
+----------------+                         +---------------+                         +--------------------+
|  company_id    |                         |  job_id       |                         |  application_id    |
|  company_name  |                         |  company_id(FK)                         |  job_id (FK)       |
|  industry      |                         |  job_title    |                         |  application_date  |
|  website       |                         |  job_type     |                         |  status (ENUM)     |
|  city, state   |                         |  salary_min   |                         |  resume_version    |
|  notes         |                         |  salary_max   |                         |  cover_letter_sent |
+----------------+                         |  requirements |                         |  interview_data    |
        |                                  |   (JSON)      |                         |   (JSON)           |
        | 1 : N                            +---------------+                         +--------------------+
        v
+----------------+
|    contacts    |
+----------------+
|  contact_id    |
|  company_id(FK)|
|  contact_name  |
|  title         |
|  email, phone  |
|  linkedin_url  |
|  notes         |
+----------------+
```

### Table Breakdown:
1. **`companies`**: Primary organization profiles.
2. **`jobs`**: Roles linked to companies (`ON DELETE CASCADE`), featuring native `JSON` array for requirements.
3. **`applications`**: Application milestones linked to jobs (`ON DELETE CASCADE`), with ENUM pipeline statuses and `JSON` interview notes.
4. **`contacts`**: Recruiter network linked to companies (`ON DELETE CASCADE`).

---

## Project Structure

```
job_tracker/
├── app.py              # Main Flask application & routing logic
├── database.py         # MySQL connection management & dictionary cursor helpers
├── schema.sql          # Database DDL script with tables & initial seed data
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable configuration template
├── README.md           # Setup and project documentation
├── AI_USAGE.md         # Generative AI usage attribution & reflection
├── static/
│   └── style.css       # Custom modern responsive styling
└── templates/
    ├── base.html       # Base layout, navbar, alert banners, and footer
    ├── dashboard.html  # KPI metric cards, pipeline counts, interview timeline
    ├── companies.html  # Companies CRUD interface with search
    ├── jobs.html       # Jobs CRUD interface with JSON requirement pills
    ├── applications.html # Applications CRUD interface with status filters
    ├── contacts.html   # Contacts directory CRUD interface
    └── job_match.html  # Skill Match algorithm and ranking interface
```

---

## Prerequisites

Before starting, ensure you have:
1. **Python 3.10+** installed: [python.org](https://www.python.org/downloads/)
2. **MySQL Server 8.0+** running locally (or via XAMPP / Docker): [mysql.com](https://dev.mysql.com/downloads/installer/)
3. **Git** for version control.

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/job_tracker.git
cd job_tracker
```

### 2. Create and Activate a Virtual Environment
**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```
**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create and Seed the MySQL Database
Open MySQL Command Line Client or MySQL Workbench and run:
```sql
SOURCE path/to/job_tracker/schema.sql;
```
*Alternatively, run via terminal:*
```bash
mysql -u root -p < schema.sql
```
This script creates the `job_tracker` database, all four tables with constraints, and realistic seed data for testing.

### 5. Configure Database Credentials
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` in your editor and adjust your MySQL password:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_ACTUAL_MYSQL_PASSWORD
DB_NAME=job_tracker
```

---

## Running the Application

Start the Flask development server:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
The navbar will indicate `MySQL Connected` in green if your credentials and database are active.

---

## Features Walkthrough

### 1. Executive Dashboard (`/`)
- Real-time KPI cards displaying Total Applications, Screening, Interviews, Offers, Active Jobs, and Companies.
- Table of recent submissions with direct link to details.
- Timeline of interview rounds dynamically parsed from JSON records.

### 2. Companies CRUD (`/companies`)
- **Create**: Add company with name, industry, website, location, and notes.
- **Read**: List of all companies with dynamic badge counts of linked jobs and contacts. Includes real-time search filter.
- **Update**: Modal edit interface with validation.
- **Delete**: Confirmation modal warning about cascade deletion.

### 3. Jobs CRUD (`/jobs`)
- **Create**: Add new roles, salary bands (`min` and `max`), and comma-separated skills (automatically converted to JSON array).
- **Read**: Clean table with currency formatting and skill pills.
- **Update / Delete**: Full modal controls with foreign key integrity.

### 4. Applications CRUD (`/applications`)
- **Create & Read**: Track jobs by application date, status badge, resume filename, and cover letter boolean.
- **Interview Rounds (JSON)**: Store multi-round interviews with dates and notes in native JSON format.
- **Status Filter**: Filter between Applied, Screening, Interview, Offer, Rejected, and Withdrawn.

### 5. Recruiter Contacts CRUD (`/contacts`)
- **Directory**: Store direct recruiters and hiring managers with mailto and phone links, LinkedIn URLs, and meeting notes.

### 6. Job Match Engine (`/job-match`)
- Enter your skills (e.g. `Python, SQL, Flask`).
- The algorithm compares your inputs against the `requirements` JSON list of each job:
  $$\text{Match Percentage} = \left(\frac{\text{Matched Skills Count}}{\text{Total Required Skills Count}}\right) \times 100$$
- Displays a ranked list from highest to lowest match score, with green pills for skills you have and red/pink pills for skills to learn next.

---

## Video Recording Submission Checklist

Per the course instructions:
> *A 3 to 7-minute recorded video file of the execution of your project (client, server, database) is required. If you do not upload this video file, your project will not be graded. Narration over the video is optional.*

### Suggested Video Flow:
1. **Database (1 min)**:
   - Open MySQL Workbench / CLI. Show `USE job_tracker; SHOW TABLES;` and `SELECT * FROM applications LIMIT 3;` demonstrating the 4 tables and JSON columns.
2. **Server (30 sec)**:
   - Show terminal launching Flask: `python app.py` running on `http://127.0.0.1:5000`.
3. **Client Walkthrough (3-4 mins)**:
   - **Dashboard**: Highlight KPI stat cards and interview timeline.
   - **Companies**: Add a new company, edit it, and show the search bar.
   - **Jobs**: Add a job with comma-separated skills; verify skill pills appear.
   - **Applications**: Track an application, change status to `Interview`, log interview notes.
   - **Job Match**: Enter skills (`Python, SQL, Flask`), run calculation, and show the ranked % breakdown with matched vs. missing skills.
   - **Delete Operation**: Demonstrate delete confirmation modal.

Upload the recorded MP4 file to your repository root or provide a direct downloadable link as required by the course instructions.

---

## GenAI Documentation

In accordance with course guidelines, full documentation of Generative AI tools (ChatGPT, Claude, Gemini), sample prompts, modifications, and lessons learned is provided in [AI_USAGE.md](AI_USAGE.md).
