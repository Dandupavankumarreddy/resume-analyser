# AI Resume Analyzer 📄✨
### Intelligent Resume Scoring, ATS Matcher & Skill Gap Recommendation Engine

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/Academic-Project-success.svg)]()

---

## 📌 Problem Statement
Job seekers and college students frequently struggle with getting shortlisted for technical roles due to automated **Applicant Tracking Systems (ATS)** and mismatched skill keywords. Resumes often lack quantifiable metrics, contain passive language, or omit crucial competencies required by specific job descriptions.

**AI Resume Analyzer** solves this problem by providing an automated, AI and NLP-powered platform that analyzes resumes, calculates an objective 100-point resume quality score, checks ATS compatibility, compares skills against targeted job roles or custom job descriptions, and provides concrete, actionable recommendations for improvement.

---

## 🌟 Key Features

### 1. Multi-Format Resume Upload & Parsing
- Supports **PDF**, **DOCX**, and **TXT** resume formats.
- Extracts candidate name, contact numbers, email addresses, and professional profiles (**LinkedIn**, **GitHub**, **Portfolio**).
- Delineates core resume sections (*Summary, Education, Technical Skills, Projects, Work Experience, Certifications*).

### 2. Multi-Dimensional 100-Point Scoring Rubric
Evaluates resumes across 5 weighted categories:
- **Skills & Keyword Match (25 Points):** Core skill density and alignment with target role.
- **Formatting & Structure (20 Points):** Section completeness, bullet point usage, contact details, and length.
- **Projects Quality & Depth (20 Points):** Technical rigor, live demo/repository links, and quantifiable impact.
- **Work Experience & Internships (20 Points):** Practical industry experience and strong action verb density.
- **Education & Qualifications (15 Points):** Degree, major, academic percentage/CGPA, and graduation timeline.

### 3. Role Matching & Skill Gap Analysis
- **Pre-Tuned Tech Roles:**
  - Python Developer
  - Full Stack Web Developer (MERN / Full Stack)
  - Data Analyst
  - AI / Machine Learning Engineer
  - DevOps & Cloud Engineer
  - Mobile App Developer (Flutter / React Native)
  - Cybersecurity Analyst
  - QA / Test Automation Engineer
- **Custom Job Description Matcher:** Paste any custom job description from LinkedIn or Indeed; our NLP engine dynamically extracts required skills and compares them against your resume.
- **Visual Skill Chips:** Separate display for **Matched Skills** (green checkmark), **Missing Skills** (red alert), and **Soft Skills**.

### 4. AI-Powered Suggestions & Writing Enhancements
- **Action Verbs & Grammar Review:** Flags passive phrases (e.g., *"responsible for"*, *"worked on"*, *"assisted in"*) and suggests high-impact power verbs (*"Spearheaded"*, *"Engineered"*, *"Optimized"*).
- **Personal Pronoun Checker:** Flags first-person pronouns (*"I"*, *"my"*, *"we"*) for an objective tone.
- **Google XYZ Metric Formula:** Recommends rewriting bullets as: *"Accomplished [X] as measured by [Y]%, by implementing [Z]"*.
- **Tailored Project & Certification Ideas:** Recommends specific project architectures and industry certifications aligned with the target role.
- **Optional Gemini LLM Integration:** Add a free Google Gemini API key in Settings for live recruiter critique and predicted interview questions.

### 5. History & SQLite Persistence
- Stores all evaluated resumes, scores, skill matrices, and suggestions in an embedded **SQLite** database (`resume_analyzer.db`).
- Interactive dashboard to revisit previous analysis reports or delete old records.
- Real-time dashboard statistics tracking average candidate scores and top roles.

### 6. Modern Responsive UI & PDF Export
- Clean glassmorphism dashboard built with **Bootstrap 5.3**, **Chart.js** (circular score gauge), and **FontAwesome 6**.
- **Dark / Light mode** toggle with persistent user preference.
- 1-Click test buttons with pre-loaded sample resumes (**Python Dev**, **Web Dev**, **Data Analyst**).
- Built-in **Print / PDF Report** generator for offline reviews.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js, FontAwesome 6 |
| **Backend** | Python 3.12, Flask 3.1, Werkzeug, Jinja2 |
| **NLP & Text Parsing** | `pypdf`, `python-docx`, `reportlab`, Regex Tokenizers, Statistical NLP |
| **AI Integration** | Local Rule-based NLP Engine + Optional Google Gemini 1.5 Flash API |
| **Database** | SQLite 3 |

---

## 📂 Project Directory Structure

```
pavan/
│
├── app.py                     # Main Flask web application server & REST API
├── database.py                # SQLite database manager & CRUD operations
├── run.py                     # Python runner with auto-browser launch
├── run.bat                    # Windows 1-click launch batch script
├── requirements.txt           # Project dependencies
├── README.md                  # Comprehensive documentation
├── resume_analyzer.db         # SQLite database file
│
├── analyzer/                  # Core Analysis & NLP Modules
│   ├── __init__.py
│   ├── parser.py              # PDF/DOCX text & contact extractor
│   ├── nlp_engine.py          # 500+ Skill taxonomy & education extractor
│   ├── job_roles.py           # Benchmark role profiles & required skills
│   ├── matcher.py             # Role & custom JD skill matching
│   ├── scorer.py              # Multi-dimensional 100-point scoring engine
│   ├── ai_suggestions.py      # Weak verb flags & content recommendations
│   └── gemini_ai.py           # Optional Gemini LLM deep critique
│
├── sample_resumes/            # Pre-made realistic resumes for testing
│   ├── sample_python_developer.docx
│   ├── sample_web_developer.pdf
│   ├── sample_data_analyst.txt
│   └── generate_samples.py
│
├── templates/
│   └── index.html             # Single-page dashboard application
│
├── static/
│   ├── css/
│   │   └── style.css          # Responsive design, gradients & print CSS
│   └── js/
│       └── main.js            # Fetch API, Chart.js gauge, history & UI logic
│
└── uploads/                   # Stored uploaded resumes
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.12 installed)
- Web browser (Chrome, Edge, Firefox)

### 2. Run the Application
You can start the server using either method:

#### Method A: Double-Click Batch File (Windows)
Double-click `run.bat` in the project folder.

#### Method B: Terminal / Command Prompt
```powershell
python run.py
```
Or directly with Flask:
```powershell
python app.py
```

### 3. Open in Browser
Visit **`http://127.0.0.1:5000`** in your browser.

---

## 🧪 Testing the Application

We have included pre-configured demo resumes and an automated test suite:

### 1-Click Demo Testing via UI
On the web dashboard, click any of the sample buttons:
- **Python Dev (DOCX)**
- **Full Stack Web (PDF)**
- **Data Analyst (TXT)**

### Automated Test Suite
Run the unit tests verifying all extraction, scoring, and API pipelines:
```powershell
python test_app.py
```
Output:
```
..........
----------------------------------------------------------------------
Ran 10 tests in 1.62s

OK
[PASS] DOCX extraction passed.
[PASS] PDF extraction passed.
[PASS] TXT extraction passed.
[PASS] Contact extraction passed.
[PASS] Skills extraction passed.
[PASS] Role matching passed.
[PASS] Resume scoring passed.
[PASS] AI Suggestions passed.
[PASS] Database CRUD operations verified.
[PASS] Flask API routes tested successfully.
```

---

## 🎓 Academic Viva & Presentation Highlights

When demonstrating this project for academic evaluations:
1. **Explain the Extraction Pipeline:** Walk through `analyzer/parser.py` explaining how PDF text streams and DOCX XML document trees are parsed without data loss.
2. **Explain the NLP Skill Engine:** Describe how `analyzer/nlp_engine.py` applies tokenization and word-boundary matching over a domain-categorized taxonomy of 500+ technical skills.
3. **Showcase the Scoring Formula:** Highlight the transparency of `analyzer/scorer.py` (Formatting: 20pts, Skills: 25pts, Projects: 20pts, Experience: 20pts, Education: 15pts).
4. **Demonstrate Custom Job Matching:** Copy a real job posting from LinkedIn and paste it into the "Custom Job Description" box to show real-time dynamic requirement extraction.
5. **Show Database Persistence:** Show how SQLite logs all analyses and allows instant retrieval from the History table.

---

## 📄 License
Developed for academic, research, and educational purposes.
