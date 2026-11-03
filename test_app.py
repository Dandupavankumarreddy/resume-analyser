"""
Automated Comprehensive Test Suite for AI Resume Analyzer
Verifies all modules, parsing pipelines, role matchers, scoring algorithms, and Flask API endpoints.
"""

import os
import sys
import unittest
import json

from analyzer.parser import extract_resume_text, extract_contact_info, extract_sections
from analyzer.nlp_engine import extract_skills, extract_education_details, estimate_experience_level, extract_project_metrics
from analyzer.job_roles import JOB_ROLES, get_role_data, list_available_roles
from analyzer.matcher import match_resume_with_role
from analyzer.scorer import calculate_resume_score
from analyzer.ai_suggestions import analyze_grammar_and_style, generate_content_improvements
from database import init_db, save_analysis, get_recent_analyses, get_analysis_by_id, delete_analysis, get_dashboard_stats
from app import app

class TestAIResumeAnalyzer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_resumes")
        cls.docx_path = os.path.join(cls.samples_dir, "sample_python_developer.docx")
        cls.pdf_path = os.path.join(cls.samples_dir, "sample_web_developer.pdf")
        cls.txt_path = os.path.join(cls.samples_dir, "sample_data_analyst.txt")
        cls.client = app.test_client()

    def test_01_extract_docx(self):
        """Test DOCX extraction."""
        self.assertTrue(os.path.exists(self.docx_path), "sample_python_developer.docx should exist")
        text = extract_resume_text(self.docx_path)
        self.assertGreater(len(text), 100)
        self.assertIn("PAVAN KUMAR", text.upper())
        self.assertIn("PYTHON", text.upper())
        print("[PASS] DOCX extraction passed. Length:", len(text))

    def test_02_extract_pdf(self):
        """Test PDF extraction."""
        self.assertTrue(os.path.exists(self.pdf_path), "sample_web_developer.pdf should exist")
        text = extract_resume_text(self.pdf_path)
        self.assertGreater(len(text), 100)
        self.assertIn("PRIYA SHARMA", text.upper())
        self.assertIn("REACT", text.upper())
        print("[PASS] PDF extraction passed. Length:", len(text))

    def test_03_extract_txt(self):
        """Test TXT extraction."""
        self.assertTrue(os.path.exists(self.txt_path), "sample_data_analyst.txt should exist")
        text = extract_resume_text(self.txt_path)
        self.assertGreater(len(text), 100)
        self.assertIn("ANANYA VERMA", text.upper())
        self.assertIn("SQL", text.upper())
        print("[PASS] TXT extraction passed. Length:", len(text))

    def test_04_contact_extraction(self):
        """Test contact information extraction."""
        text = extract_resume_text(self.docx_path)
        contact = extract_contact_info(text)
        self.assertEqual(contact["name"], "Pavan Kumar")
        self.assertEqual(contact["email"], "pavan.kumar@example.com")
        self.assertIn("98765", contact["phone"])
        self.assertIn("github.com", contact["github"])
        self.assertIn("linkedin.com", contact["linkedin"])
        print("[PASS] Contact extraction passed:", contact)

    def test_05_skill_extraction(self):
        """Test technical and soft skill extraction."""
        text = extract_resume_text(self.docx_path)
        skills = extract_skills(text)
        self.assertIn("python", skills["technical_flat"])
        self.assertIn("django", skills["technical_flat"])
        self.assertIn("postgresql", skills["technical_flat"])
        self.assertGreater(len(skills["soft_skills"]), 0)
        print("[PASS] Skills extraction passed. Technical skills count:", len(skills["technical_flat"]), "Soft skills:", skills["soft_skills"])

    def test_06_role_matching(self):
        """Test matching resume against target role."""
        text = extract_resume_text(self.docx_path)
        skills = extract_skills(text)
        match_res = match_resume_with_role(skills, "python_developer")
        self.assertGreater(match_res["core_match_pct"], 40)
        self.assertIn("Python", match_res["matched_core_skills"])
        print(f"[PASS] Role matching passed. Match: {match_res['core_match_pct']}% for {match_res['target_role_title']}")

    def test_07_resume_scoring(self):
        """Test weighted scoring out of 100."""
        text = extract_resume_text(self.docx_path)
        contact = extract_contact_info(text)
        sections = extract_sections(text)
        skills = extract_skills(text)
        role_matching = match_resume_with_role(skills, "python_developer")
        experience = estimate_experience_level(text, sections)
        projects = extract_project_metrics(text, sections)
        education = extract_education_details(text)
        
        score_data = calculate_resume_score(
            contact, sections, skills, role_matching, experience, projects, education, len(text.split())
        )
        self.assertGreaterEqual(score_data["overall_score"], 60)
        self.assertLessEqual(score_data["overall_score"], 100)
        self.assertIn("categories", score_data)
        print("[PASS] Resume scoring passed. Overall score:", score_data["overall_score"], "Grade:", score_data["grade"])

    def test_08_grammar_and_suggestions(self):
        """Test grammar and AI suggestions generator."""
        text = extract_resume_text(self.docx_path)
        sections = extract_sections(text)
        grammar = analyze_grammar_and_style(text, sections)
        self.assertIn("issues", grammar)

        role_data = get_role_data("python_developer")
        skills = extract_skills(text)
        role_matching = match_resume_with_role(skills, "python_developer")
        suggestions = generate_content_improvements(text, sections, role_data, role_matching)
        self.assertGreater(len(suggestions), 0)
        print("[PASS] AI Suggestions passed. Total suggestions:", len(suggestions))

    def test_09_database_crud(self):
        """Test SQLite database operations."""
        stats_before = get_dashboard_stats()
        contact = {"name": "Test User", "email": "test@test.com", "phone": "1234567890"}
        record_id = save_analysis(
            filename="test_resume.pdf",
            parsed_contact=contact,
            target_role="Full Stack Developer",
            score_data={"overall_score": 85, "grade": "Excellent", "ats_verdict": "High", "categories": {}},
            role_matching={"core_match_pct": 80, "matched_core_skills": ["Python"], "missing_core_skills": []},
            skills_data={"soft_skills": ["Teamwork"]},
            suggestions=[],
            grammar_data={"issues": []},
            word_count=450,
            raw_text="Sample raw resume content"
        )
        self.assertIsNotNone(record_id)
        
        fetched = get_analysis_by_id(record_id)
        self.assertEqual(fetched["candidate_name"], "Test User")
        self.assertEqual(fetched["overall_score"], 85)

        deleted = delete_analysis(record_id)
        self.assertTrue(deleted)
        print("[PASS] Database CRUD operations verified.")

    def test_10_api_endpoints(self):
        """Test Flask REST API routes."""
        # GET /
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)
        self.assertIn(b"AI Resume", res_home.data)

        # GET /api/roles
        res_roles = self.client.get("/api/roles")
        self.assertEqual(res_roles.status_code, 200)
        roles_json = json.loads(res_roles.data)
        self.assertTrue(roles_json["success"])
        self.assertIn("python_developer", roles_json["roles"])

        # GET /api/stats
        res_stats = self.client.get("/api/stats")
        self.assertEqual(res_stats.status_code, 200)

        # POST /api/analyze-sample
        res_sample = self.client.post("/api/analyze-sample", json={
            "sample_key": "python_dev",
            "role_key": "python_developer"
        })
        self.assertEqual(res_sample.status_code, 200)
        sample_json = json.loads(res_sample.data)
        self.assertTrue(sample_json["success"])
        self.assertEqual(sample_json["data"]["contact_info"]["name"], "Pavan Kumar")
        self.assertGreater(sample_json["data"]["scoring"]["overall_score"], 50)
        print("[PASS] Flask API routes tested successfully. Sample analysis score:", sample_json["data"]["scoring"]["overall_score"])

if __name__ == "__main__":
    unittest.main()
