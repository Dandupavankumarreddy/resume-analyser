"""
AI Resume Analyzer - Flask Web Application
Main server handling resume uploads, parsing, role matching, AI evaluation, and SQLite persistence.
"""

import os
import json
import uuid
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory

from analyzer.parser import extract_resume_text, extract_contact_info, extract_sections
from analyzer.nlp_engine import extract_skills, extract_education_details, estimate_experience_level, extract_project_metrics
from analyzer.job_roles import JOB_ROLES, list_available_roles, get_role_data
from analyzer.matcher import match_resume_with_role
from analyzer.scorer import calculate_resume_score
from analyzer.ai_suggestions import analyze_grammar_and_style, generate_content_improvements
from analyzer.gemini_ai import call_gemini_for_enhancement
from database import init_db, save_analysis, get_recent_analyses, get_analysis_by_id, delete_analysis, get_dashboard_stats

app = Flask(__name__)
app.config["SECRET_KEY"] = "ai-resume-analyzer-secret-key-2026"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 # 16 MB max limit
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize SQLite database
init_db()

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    """Renders the main modern dashboard UI."""
    roles = list_available_roles()
    stats = get_dashboard_stats()
    return render_template("index.html", roles=roles, stats=stats)

@app.route("/api/roles", methods=["GET"])
def get_roles():
    """Returns available benchmark roles."""
    return jsonify({
        "success": True,
        "roles": JOB_ROLES
    })

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Returns database summary statistics."""
    stats = get_dashboard_stats()
    return jsonify({"success": True, "stats": stats})

@app.route("/api/history", methods=["GET"])
def get_history():
    """Returns past resume analysis history."""
    limit = request.args.get("limit", default=30, type=int)
    history = get_recent_analyses(limit=limit)
    return jsonify({"success": True, "history": history})

@app.route("/api/analysis/<int:analysis_id>", methods=["GET"])
def get_single_analysis(analysis_id):
    """Retrieves full analysis report for a given record."""
    data = get_analysis_by_id(analysis_id)
    if not data:
        return jsonify({"success": False, "error": "Analysis not found"}), 404
    return jsonify({"success": True, "data": data})

@app.route("/api/analysis/<int:analysis_id>", methods=["DELETE"])
def remove_analysis(analysis_id):
    """Deletes an analysis record from database."""
    deleted = delete_analysis(analysis_id)
    return jsonify({"success": deleted})

def process_resume_content(raw_text: str, filename: str, role_key: str, custom_jd: str = "", api_key: str = "") -> dict:
    """Core analysis orchestrator pipeline."""
    if not raw_text or len(raw_text.strip()) < 15:
        raise ValueError(
            "Could not extract legible text from your resume file. "
            "Please ensure your PDF or DOCX contains selectable text (not an unreadable scan or blank document)."
        )

    # 1. Contact & Sections Extraction
    contact_info = extract_contact_info(raw_text)
    sections = extract_sections(raw_text)
    words = raw_text.split()
    word_count = len(words)

    # 2. Skill Extraction (Technical & Soft)
    skills_data = extract_skills(raw_text)

    # 3. Education, Experience & Projects Extraction
    education_data = extract_education_details(raw_text)
    experience_data = estimate_experience_level(raw_text, sections)
    project_metrics = extract_project_metrics(raw_text, sections)

    # 4. Job Role Matching
    role_matching = match_resume_with_role(skills_data, role_key, custom_jd)

    # 5. Multi-dimensional Scoring (Out of 100)
    score_result = calculate_resume_score(
        parsed_contact=contact_info,
        sections=sections,
        skills_data=skills_data,
        role_matching=role_matching,
        experience_data=experience_data,
        project_metrics=project_metrics,
        education_data=education_data,
        word_count=word_count
    )

    # 6. Grammar & AI Suggestions
    grammar_data = analyze_grammar_and_style(raw_text, sections)
    role_data = get_role_data(role_key)
    content_suggestions = generate_content_improvements(raw_text, sections, role_data, role_matching)

    # 7. Optional Gemini LLM Deep Critique
    gemini_result = call_gemini_for_enhancement(
        resume_text=raw_text,
        target_role=role_matching["target_role_title"],
        matched_skills=role_matching["matched_core_skills"],
        missing_skills=role_matching["missing_core_skills"],
        api_key=api_key
    )

    # 8. Save to SQLite Database
    analysis_id = save_analysis(
        filename=filename,
        parsed_contact=contact_info,
        target_role=role_matching["target_role_title"],
        score_data=score_result,
        role_matching=role_matching,
        skills_data=skills_data,
        suggestions=content_suggestions,
        grammar_data=grammar_data,
        word_count=word_count,
        raw_text=raw_text
    )

    return {
        "analysis_id": analysis_id,
        "filename": filename,
        "contact_info": contact_info,
        "education": education_data,
        "experience": experience_data,
        "projects": project_metrics,
        "skills": skills_data,
        "role_matching": role_matching,
        "scoring": score_result,
        "grammar_and_style": grammar_data,
        "suggestions": content_suggestions,
        "gemini_critique": gemini_result,
        "word_count": word_count,
        "sections_detected": list(sections.keys())
    }

@app.route("/api/analyze", methods=["POST"])
def analyze_resume_endpoint():
    """Handles file upload and executes analysis."""
    if "resume" not in request.files:
        return jsonify({"success": False, "error": "No resume file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file type. Please upload a PDF or DOCX file."}), 400

    role_key = request.form.get("role_key", "python_developer")
    custom_jd = request.form.get("custom_jd", "")
    api_key = request.form.get("api_key", "")

    # Save file
    orig_filename = secure_filename(file.filename) or "resume.pdf"
    unique_filename = f"{uuid.uuid4().hex[:8]}_{orig_filename}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(file_path)

    try:
        raw_text = extract_resume_text(file_path)
        print(f"[ANALYZE] Extracted {len(raw_text)} chars from: {orig_filename}")
        result = process_resume_content(
            raw_text=raw_text,
            filename=orig_filename,
            role_key=role_key,
            custom_jd=custom_jd,
            api_key=api_key
        )
        return jsonify({"success": True, "data": result})
    except ValueError as ve:
        print(f"[ANALYZE ERROR] {ve}")
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        print(f"[ANALYZE ERROR] Unexpected: {e}")
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"}), 500

@app.route("/api/analyze-sample", methods=["POST"])
def analyze_sample_endpoint():
    """Instantly analyzes one of the pre-loaded sample resumes."""
    data = request.get_json() or {}
    sample_key = data.get("sample_key", "python_dev")
    role_key = data.get("role_key", "python_developer")
    api_key = data.get("api_key", "")

    sample_mapping = {
        "python_dev": ("sample_python_developer.txt", "python_developer", "Pavan_Kumar_Python_Resume.txt"),
        "web_dev": ("sample_web_developer.txt", "web_developer", "Priya_Sharma_WebDev_Resume.txt"),
        "data_analyst": ("sample_data_analyst.txt", "data_analyst", "Ananya_Verma_DataAnalyst_Resume.txt")
    }

    if sample_key not in sample_mapping:
        sample_key = "python_dev"

    sample_file, default_role, display_name = sample_mapping[sample_key]
    selected_role = role_key if role_key else default_role
    sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_resumes", sample_file)

    if not os.path.exists(sample_path):
        return jsonify({"success": False, "error": "Sample file not found"}), 404

    with open(sample_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    try:
        result = process_resume_content(
            raw_text=raw_text,
            filename=display_name,
            role_key=selected_role,
            api_key=api_key
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting AI Resume Analyzer on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
