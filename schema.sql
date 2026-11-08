-- ============================================================
-- Job Application Tracker - Database Schema & Seed Data
-- ============================================================

CREATE DATABASE IF NOT EXISTS job_tracker;
USE job_tracker;

-- Drop existing tables to ensure clean rebuild (respecting FK constraints)
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;

-- ------------------------------------------------------------
-- 1. COMPANIES TABLE
-- ------------------------------------------------------------
CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    website VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 2. JOBS TABLE
-- ------------------------------------------------------------
CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    job_type ENUM('Full-time', 'Part-time', 'Contract', 'Internship') DEFAULT 'Full-time',
    salary_min INT,
    salary_max INT,
    job_url VARCHAR(300),
    date_posted DATE,
    requirements JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 3. APPLICATIONS TABLE
-- ------------------------------------------------------------
CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    application_date DATE NOT NULL,
    status ENUM('Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn') DEFAULT 'Applied',
    resume_version VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    interview_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_applications_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 4. CONTACTS TABLE
-- ------------------------------------------------------------
CREATE TABLE contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_contacts_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SEED DATA FOR DEMO & TESTING
-- ============================================================

-- Seed Companies
INSERT INTO companies (company_id, company_name, industry, website, city, state, notes) VALUES
(1, 'TechCorp Solutions', 'Technology / SaaS', 'https://techcorp-solutions.example.com', 'Miami', 'FL', 'Fast-growing cloud software provider. Met recruiter at FIU career fair.'),
(2, 'FinData Analytics', 'FinTech', 'https://findata.example.com', 'New York', 'NY', 'Institutional finance data analytics platform. Strong engineering culture.'),
(3, 'HealthBridge Systems', 'Healthcare Tech', 'https://healthbridge.example.com', 'Austin', 'TX', 'HIPAA compliant telemetry and patient management portal.'),
(4, 'NextGen Mobile', 'E-Commerce / Retail', 'https://nextgenmobile.example.com', 'Seattle', 'WA', 'High-traffic mobile commerce and fulfillment logistics.');

-- Seed Jobs
INSERT INTO jobs (job_id, company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 1, 'Junior Software Engineer', 'Full-time', 75000, 95000, 'https://techcorp-solutions.example.com/careers/jr-swe', '2026-10-15', '["Python", "Flask", "MySQL", "Git", "REST APIs"]'),
(2, 1, 'Backend Developer', 'Full-time', 90000, 115000, 'https://techcorp-solutions.example.com/careers/backend-dev', '2026-10-20', '["Python", "Docker", "MySQL", "AWS", "FastAPI"]'),
(3, 2, 'Data Analyst', 'Full-time', 70000, 88000, 'https://findata.example.com/jobs/data-analyst', '2026-10-25', '["SQL", "Python", "Tableau", "Excel", "Data Modeling"]'),
(4, 3, 'Full Stack Intern', 'Internship', 50000, 60000, 'https://healthbridge.example.com/interns/fullstack', '2026-11-01', '["HTML", "CSS", "JavaScript", "Python", "MySQL"]'),
(5, 4, 'Cloud Infrastructure Engineer', 'Contract', 95000, 130000, 'https://nextgenmobile.example.com/careers/cloud-infra', '2026-11-03', '["Linux", "AWS", "Docker", "Kubernetes", "Terraform"]');

-- Seed Applications
INSERT INTO applications (application_id, job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, 1, '2026-10-18', 'Interview', 'SWE_Resume_v3.pdf', TRUE, '[{"round": "Recruiter Screen", "date": "2026-10-22", "notes": "30-min call with Sarah. Discussed Flask projects and graduation date."}, {"round": "Technical Assessment", "date": "2026-10-29", "notes": "90-minute live coding in Python: SQL query optimization and REST API endpoints."}]'),
(2, 2, '2026-10-24', 'Screening', 'SWE_Resume_v3.pdf', TRUE, '[{"round": "HR Pre-Screen", "date": "2026-11-02", "notes": "Confirmed salary expectations and remote work availability."}]'),
(3, 3, '2026-10-28', 'Applied', 'Data_Resume_v2.pdf', FALSE, '[]'),
(4, 4, '2026-11-02', 'Offer', 'General_Resume_v1.pdf', TRUE, '[{"round": "Manager Behavioral", "date": "2026-11-05", "notes": "Interview with engineering manager. Discussed team fit and summer timeline."}, {"round": "Offer Received", "date": "2026-11-07", "notes": "Received written offer letter for Summer 2027 internship!"}]');

-- Seed Contacts
INSERT INTO contacts (contact_id, company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 1, 'Sarah Jenkins', 'Technical Talent Partner', 'sjenkins@techcorp-solutions.example.com', '305-555-0192', 'https://linkedin.com/in/sarahjenkins-recruiter', 'Primary recruiter for campus hiring and SWE roles.'),
(2, 1, 'David Alvarez', 'Lead Backend Architect', 'dalvarez@techcorp-solutions.example.com', '305-555-0144', 'https://linkedin.com/in/davidalvarez-dev', 'Interviewer for second technical round.'),
(3, 2, 'Elena Rostova', 'Head of People Operations', 'erostova@findata.example.com', '212-555-0811', 'https://linkedin.com/in/elenarostova-hr', 'Messaged through LinkedIn message following job posting.'),
(4, 3, 'Marcus Vance', 'VP of Engineering', 'mvance@healthbridge.example.com', '512-555-3390', 'https://linkedin.com/in/marcusvance-vp', 'Met at Healthcare Hackathon keynote.');
