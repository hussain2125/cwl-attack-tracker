#!/usr/bin/env python3
"""
Script to check static file accessibility and permissions
Run this on your EC2 instance to diagnose static file issues
"""

import os
import stat

def check_static_files():
    print("=== Static File Check ===")
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check if static folder exists
    static_folder = 'static'
    if os.path.exists(static_folder):
        print(f"✓ Static folder exists: {static_folder}")
        
        # Check static folder permissions
        static_perms = oct(stat.S_IMODE(os.lstat(static_folder).st_mode))
        print(f"Static folder permissions: {static_perms}")
        
        # List files in static folder
        files = os.listdir(static_folder)
        print(f"Files in static folder: {files}")
        
        # Check style.css specifically
        css_file = os.path.join(static_folder, 'style.css')
        if os.path.exists(css_file):
            print(f"✓ style.css exists: {css_file}")
            
            # Check file permissions
            css_perms = oct(stat.S_IMODE(os.lstat(css_file).st_mode))
            print(f"style.css permissions: {css_perms}")
            
            # Check file size
            file_size = os.path.getsize(css_file)
            print(f"style.css size: {file_size} bytes")
            
            # Check if file is readable
            try:
                with open(css_file, 'r') as f:
                    first_line = f.readline().strip()
                print(f"✓ style.css is readable, first line: {first_line[:50]}...")
            except Exception as e:
                print(f"✗ Error reading style.css: {e}")
        else:
            print(f"✗ style.css not found: {css_file}")
            
        # Check town_hall folder
        town_hall_folder = os.path.join(static_folder, 'town_hall')
        if os.path.exists(town_hall_folder):
            print(f"✓ town_hall folder exists")
            town_hall_files = os.listdir(town_hall_folder)
            print(f"Town hall files: {len(town_hall_files)} files")
        else:
            print(f"✗ town_hall folder not found")
    else:
        print(f"✗ Static folder not found: {static_folder}")
    
    print("\n=== Flask App Check ===")
    try:
        from app import app
        print(f"✓ Flask app loaded successfully")
        print(f"Static folder: {app.static_folder}")
        print(f"Static URL path: {app.static_url_path}")
        
        # Test static file serving
        with app.test_client() as client:
            response = client.get('/static/style.css')
            print(f"Static file response status: {response.status_code}")
            if response.status_code == 200:
                print(f"✓ Static file serving works")
            else:
                print(f"✗ Static file serving failed: {response.status_code}")
                
    except Exception as e:
        print(f"✗ Error loading Flask app: {e}")

if __name__ == "__main__":
    check_static_files() 