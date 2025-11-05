"""
Script to take a screenshot of the styled interface
"""

import time
import sqlite3
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys

def create_test_session():
    """Create a test audit session with a fixed ID for screenshot purposes"""
    # Connect to the database
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create a test session
    session_id = "test_style_session"
    session_name = "Style Test Audit"
    
    # Delete existing session if it exists
    cursor.execute("DELETE FROM audit_sessions WHERE session_id = ?", (session_id,))
    
    # Create a new session
    cursor.execute('''
        INSERT INTO audit_sessions (
            session_id, name, created_at, framework_filter, category_filter, risk_level_filter
        ) VALUES (?, ?, datetime('now'), ?, ?, ?)
    ''', (session_id, session_name, 'EU AI Law', 'All', 'All'))
    
    conn.commit()
    conn.close()
    
    print(f"Created test session with ID {session_id}")
    return session_id

def take_screenshot(session_id):
    """Take a screenshot of the styled question page"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1280,800')
    
    service = Service()
    driver = webdriver.Chrome(options=chrome_options, service=service)
    
    try:
        # Navigate to the first question of the test session
        url = f"http://localhost:5000/audit/{session_id}/question/0"
        print(f"Opening URL: {url}")
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Take a screenshot
        screenshot_path = "styled_interface.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Get the URL that was actually loaded (for debugging)
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Get the page title (for debugging)
        title = driver.title
        print(f"Page title: {title}")
        
        # Get page source (for debugging)
        page_source = driver.page_source
        print(f"Page source length: {len(page_source)} characters")
        
        return screenshot_path
    
    finally:
        driver.quit()

if __name__ == "__main__":
    session_id = create_test_session()
    screenshot_path = take_screenshot(session_id)
    print(f"Process complete. Screenshot at {screenshot_path}")