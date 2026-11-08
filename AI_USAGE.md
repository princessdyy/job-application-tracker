# AI Usage Documentation

This document records the generative AI tools, prompts, iterations, code modifications, and engineering lessons learned during the development of the **Job Application Tracker** web application.

---

## 1. Tools Used
- **Claude (Anthropic)**: Primary code architecture, relational database schema drafting, foreign key constraint planning, and Jinja2 modular templating.
- **ChatGPT (GPT-4 / OpenAI)**: Initial Flask routing boilerplate, MySQL connector dictionary cursor utilities, and query optimization.
- **Gemini (Google DeepMind)**: Job Match scoring algorithm design, fuzzy skill matching logic, and UI styling polish using Bootstrap 5.

---

## 2. Key Prompts

### Database Schema & Foreign Key Architecture
> **Prompt**:  
> *"Generate a complete MySQL 8 schema for a Job Application Tracker consisting of four tables: companies, jobs, applications, and contacts. The jobs table must store requirements as a JSON array, applications must store interview rounds/notes as JSON, and applications must enforce an ENUM status ('Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'). Include cascading foreign keys and realistic seed data."*

### Job Match Algorithm Design
> **Prompt**:  
> *"Write a Python algorithm inside a Flask route that takes a comma-separated string of user skills and compares it with job requirements stored in MySQL as a JSON list. Calculate the match percentage: (matched_skills / total_skills) * 100, identify both matched and missing skills, and sort the jobs descending by match percentage."*

### Database Connection and Context Management
> **Prompt**:  
> *"How do I structure a robust `database.py` file with `mysql-connector-python` that handles connection failures gracefully, supports dictionary cursors, and exposes a diagnostic function to check connection health in Flask?"*

### UI Responsive Design with Bootstrap 5
> **Prompt**:  
> *"Create a clean Bootstrap 5 navbar and executive dashboard layout with stat cards for total applications, interviews, and offers, plus custom badge styles for job match pills (green for matched, red for missing)."*

---

## 3. What Worked Well

- **Rapid Prototyping**: GenAI quickly produced boilerplate Flask routes and SQL statements, allowing fast transition to feature development and testing.
- **JSON Column Guidance**: GenAI provided clear examples of how MySQL 8 handles native `JSON` columns and how Python's built-in `json` module can serialize and deserialize requirements and interview rounds.
- **Algorithm Foundation**: The mathematical model for the skill match engine was drafted cleanly by AI, ensuring predictable percentage scoring and rank ordering.
- **Error Diagnosis**: When debugging SQL syntax errors and Jinja templating filters, AI provided immediate explanations of cursor lifecycles and dictionary mapping.

---

## 4. What Was Modified from AI Output

AI-generated code was not used blindly; several critical modifications, fixes, and architectural adjustments were made:

1. **Schema Integrity & Cascade Rules**:
   - *AI Initial Output*: Used generic `VARCHAR` strings for requirements and lacked explicit `ON DELETE CASCADE` clauses on child tables (`applications`, `jobs`, `contacts`).
   - *Modification*: Enforced strict `JSON` data types for `jobs.requirements` and `applications.interview_data`, added foreign key constraints with `ON DELETE CASCADE`, and implemented `COLLATE=utf8mb4_unicode_ci` for international character support.

2. **Input Sanitization & Normalization**:
   - *AI Initial Output*: Assumed skill comparisons would always be exact casing and that users would never submit whitespace or empty values.
   - *Modification*: Built robust normalization using `.strip().lower()`, converted comma- or semicolon-separated inputs into clean Python sets, and performed bidirectional substring matching so "Python" matches "Python 3" or "Python (Advanced)".

3. **Database Connection Lifecycle**:
   - *AI Initial Output*: Left connections unclosed in error scenarios and hardcoded database passwords in `app.py`.
   - *Modification*: Separated connection logic into `database.py`, integrated `python-dotenv` for secure environment variable handling, and wrapped queries in `try...finally` blocks to guarantee cursors and connections always close.

4. **User Experience & Modals**:
   - *AI Initial Output*: Provided separate bare-bones HTML pages for every Add and Edit action.
   - *Modification*: Consolidated Create and Edit operations into interactive Bootstrap 5 modals with deletion confirmation dialogs, significantly improving UX and eliminating page jumping.

---

## 5. Lessons Learned

1. **AI is an Accelerator, Not an Architect**: AI generates high-quality snippets, but the developer must define schema consistency, edge-case validation, and foreign key cascades.
2. **Always Validate Data Types**: AI frequently generates strings where structured JSON or integers are more appropriate. Explicit schema design prevents runtime type errors.
3. **Prompt Specificity Yields Better Code**: Asking for specific error handling, dictionary cursors, and case-insensitivity in the initial prompt saves substantial debugging time later.
4. **Testing After Fresh Setup is Essential**: Even when AI code looks syntactically correct, testing on a clean database clone reveals missing foreign key values, null pointer errors, and missing Jinja filters.
