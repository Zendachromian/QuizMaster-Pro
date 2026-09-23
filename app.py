import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from init_app import create_app
from extensions import db

app = create_app()

# Initialize database tables
with app.app_context():
    try:
        # Ensure instance directory exists with proper permissions
        instance_dir = os.path.join(app.instance_path)
        os.makedirs(instance_dir, exist_ok=True)
        os.chmod(instance_dir, 0o755)
        
        db.create_all()
        print("🚀 DB ready!")
    except Exception as e:
        print(f"Database initialization error: {e}")
        sys.exit(1)

@app.route('/')
def serve_blank():
    return "", 200  # blank for SPA routing

@app.route('/<path:path>')
def serve_static(path):
    # API routes only, everything else gets blank
    return "", 200

if __name__ == '__main__':
    print("🌟 QuizMaster API starting...")
    print("🔗 Backend: http://localhost:5001")
    print("🔗 Frontend: http://localhost:8080")
    print("📝 Admin: admin@quizmaster.com / admin123")
    
    # Use environment variable for debug mode, default to False
    debug_mode = os.environ.get('FLASK_DEBUG', '0').lower() in ['1', 'true', 'yes', 'on']
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5001, use_reloader=False)