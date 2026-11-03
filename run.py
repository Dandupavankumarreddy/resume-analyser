"""
Application Entrypoint
Run this script to launch the AI Resume Analyzer web server.
"""

import sys
import os
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.5)
    url = "http://127.0.0.1:5000"
    print(f"\nOpening AI Resume Analyzer in browser: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    from app import app
    print("=" * 60)
    print("      AI Resume Analyzer - Starting Application")
    print("      Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    
    # Launch browser automatically
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host="127.0.0.1", port=5000, debug=False)
