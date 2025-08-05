#!/bin/bash

echo "=== Deploying CWL War Tracker ==="

# Set proper permissions for static files
echo "Setting file permissions..."
chmod -R 755 static/
chmod 644 static/style.css
chmod 644 static/town_hall/*.png

# Check if files exist
echo "Checking file structure..."
ls -la static/
ls -la static/town_hall/ | head -5

# Set environment for production
export FLASK_ENV=production

# Run the static file check
echo "Running static file check..."
python3 check_static.py

echo "=== Deployment complete ==="
echo "To start the application:"
echo "python3 app.py"
echo ""
echo "To test static files, visit:"
echo "http://your-ec2-ip:5000/test-static" 