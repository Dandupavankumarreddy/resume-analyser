"""
Database Module
Manages SQLite storage for resume analyses, history, and metrics.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume_analyzer.db")

def get_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            candidate_name TEXT,
            email TEXT,
            phone TEXT,
            linkedin TEXT,
            github TEXT,
            target_role TEXT,
            overall_score INTEGER,
            grade TEXT,
            ats_verdict TEXT,
            core_match_pct INTEGER,
            category_scores TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            soft_skills TEXT,
            suggestions TEXT,
            grammar_issues TEXT,
            word_count INTEGER,
            raw_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(
    filename: str,
    parsed_contact: Dict[str, str],
    target_role: str,
    score_data: Dict[str, Any],
    role_matching: Dict[str, Any],
    skills_data: Dict[str, Any],
    suggestions: List[Dict[str, Any]],
    grammar_data: Dict[str, Any],
    word_count: int,
    raw_text: str
) -> int:
    """Inserts a new resume analysis record and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO analyses (
            filename, candidate_name, email, phone, linkedin, github,
            target_role, overall_score, grade, ats_verdict, core_match_pct,
            category_scores, matched_skills, missing_skills, soft_skills,
            suggestions, grammar_issues, word_count, raw_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        parsed_contact.get("name", "Candidate"),
        parsed_contact.get("email", ""),
        parsed_contact.get("phone", ""),
        parsed_contact.get("linkedin", ""),
        parsed_contact.get("github", ""),
        target_role,
        score_data.get("overall_score", 0),
        score_data.get("grade", "N/A"),
        score_data.get("ats_verdict", ""),
        role_matching.get("core_match_pct", 0),
        json.dumps(score_data.get("categories", {})),
        json.dumps(role_matching.get("matched_core_skills", [])),
        json.dumps(role_matching.get("missing_core_skills", [])),
        json.dumps(skills_data.get("soft_skills", [])),
        json.dumps(suggestions),
        json.dumps(grammar_data.get("issues", [])),
        word_count,
        raw_text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def get_recent_analyses(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetches recent analyses for dashboard history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, candidate_name, target_role, overall_score, 
               grade, core_match_pct, created_at 
        FROM analyses 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full details of a specific analysis record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    
    data = dict(row)
    # Parse JSON fields back to dicts/lists
    for json_field in ["category_scores", "matched_skills", "missing_skills", "soft_skills", "suggestions", "grammar_issues"]:
        if data.get(json_field):
            try:
                data[json_field] = json.loads(data[json_field])
            except Exception:
                data[json_field] = []
    return data

def delete_analysis(analysis_id: int) -> bool:
    """Deletes an analysis record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_dashboard_stats() -> Dict[str, Any]:
    """Computes high-level analytics for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(overall_score), MAX(overall_score), MIN(overall_score) FROM analyses")
    total_resumes, avg_score, max_score, min_score = cursor.fetchone()
    
    cursor.execute("""
        SELECT target_role, COUNT(*) as count 
        FROM analyses 
        GROUP BY target_role 
        ORDER BY count DESC 
        LIMIT 5
    """)
    popular_roles = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    return {
        "total_resumes": total_resumes or 0,
        "avg_score": round(avg_score, 1) if avg_score else 0,
        "max_score": max_score or 0,
        "popular_roles": popular_roles
    }
