#!/bin/bash

# Script to create a submission-ready zip file under 10MB
# Excludes unnecessary files and folders

echo "Creating submission zip file..."

# Remove the old zip if it exists
rm -f /mnt/e/iit_projects/m2_submission.zip

# Create zip with maximum compression, excluding heavy files
zip -r -9 /mnt/e/iit_projects/m2_submission.zip . \
    -x "venv/*" \
    -x "__pycache__/*" \
    -x "*/__pycache__/*" \
    -x "*/*/__pycache__/*" \
    -x "*.pyc" \
    -x "node_modules/*" \
    -x "frontend/node_modules/*" \
    -x "logs/*" \
    -x "uploads/*" \
    -x "*.log" \
    -x "dump.rdb" \
    -x "celerybeat-schedule" \
    -x "instance/*.db" \
    -x ".git/*" \
    -x ".vscode/*" \
    -x "*.tmp" \
    -x "*.temp" \
    -x ".cache/*" \
    -x "frontend/dist/*" \
    -x "static/dist/*"

echo "Checking zip file size..."
zip_size=$(stat -c%s "/mnt/e/iit_projects/m2_submission.zip")
zip_size_mb=$((zip_size / 1024 / 1024))

echo "Zip file created: /mnt/e/iit_projects/m2_submission.zip"
echo "Size: ${zip_size_mb} MB"

if [ $zip_size_mb -lt 10 ]; then
    echo "✅ Success! Zip file is under 10 MB"
else
    echo "⚠️  Warning: Zip file is still over 10 MB"
fi
