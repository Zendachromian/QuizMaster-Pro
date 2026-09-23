import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from extensions import db, bcrypt, jwt, cache, mail
from models import User, Subject, Chapter, Quiz, Question
# from tasks import make_celery  # Temporarily disable Celery
from datetime import datetime, timedelta

def create_app(config_name=None):
    """Create Flask application with all configurations and extensions."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    
    # JWT configuration
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=int(identity)).one_or_none()
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify(msg='Token has expired'), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(msg='Invalid token'), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(msg='Authorization token is required'), 401
    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
            "supports_credentials": True
        }
    })
    
    # Initialize Celery - temporarily disabled
    # celery = make_celery(app)
    
    # Register API blueprints
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add CORS headers for all responses
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:8080', 'http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:8080']:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # CLI commands
    @app.cli.command()
    def create_db():
        """Create database tables."""
        db.create_all()
        print("Database tables created.")
    
    @app.cli.command()
    def init_admin():
        """Initialize admin user."""
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print("Admin already exists.")
            return
        
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(
            email='admin@quizmaster.com',
            username='admin',
            full_name='Quiz Master Admin',
            password=hashed_password,
            role='admin',
            is_active=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: admin@quizmaster.com / admin123")
    
    @app.cli.command()
    def init_sample_data():
        """Initialize sample quiz data."""
        create_sample_data()
    
    return app

def init_database():
    """Initialize database with tables and sample data."""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created!")
        
        # Create admin user if not exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                email='admin@quizmaster.com',
                username='admin',
                full_name='Quiz Master Administrator',
                password=hashed_password,
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created!")
            print("   Email: admin@quizmaster.com")
            print("   Password: admin123")
        else:
            print("ℹ️  Admin user already exists")
        
        # Create sample data if no subjects exist
        if Subject.query.count() == 0:
            create_sample_data()
        
        print("🎉 Database initialization complete!")

def create_sample_data():
    """Create sample subjects, chapters, and quizzes."""
    # Sample subjects
    subjects_data = [
        {
            'name': 'Mathematics',
            'description': 'Mathematical concepts and problem solving',
            'chapters': [
                {
                    'name': 'Algebra',
                    'description': 'Basic algebraic operations and equations'
                },
                {
                    'name': 'Geometry',
                    'description': 'Shapes, angles, and spatial reasoning'
                }
            ]
        },
        {
            'name': 'Science',
            'description': 'Scientific principles and experiments',
            'chapters': [
                {
                    'name': 'Physics',
                    'description': 'Motion, energy, and matter'
                },
                {
                    'name': 'Chemistry',
                    'description': 'Elements, compounds, and reactions'
                }
            ]
        }
    ]
    
    for subject_data in subjects_data:
        subject = Subject(
            name=subject_data['name'],
            description=subject_data['description']
        )
        db.session.add(subject)
        db.session.flush()  # Get the ID
        
        for chapter_data in subject_data['chapters']:
            chapter = Chapter(
                subject_id=subject.id,
                name=chapter_data['name'],
                description=chapter_data['description'],
                order_index=1
            )
            db.session.add(chapter)
            db.session.flush()
            
            # Create a sample quiz for each chapter
            quiz = Quiz(
                chapter_id=chapter.id,
                title=f"{chapter_data['name']} Basics",
                description=f"Basic concepts in {chapter_data['name']}",
                date_of_quiz=datetime.utcnow() + timedelta(hours=1),
                time_duration=30,  # 30 minutes
                max_attempts=3,
                passing_score=60
            )
            db.session.add(quiz)
            db.session.flush()
            
            # Add sample questions
            sample_questions = [
                {
                    'question_text': f'What is the basic principle of {chapter_data["name"]}?',
                    'option_a': 'Option A',
                    'option_b': 'Option B', 
                    'option_c': 'Option C',
                    'option_d': 'Option D',
                    'correct_option': 'A'
                },
                {
                    'question_text': f'Which of the following is true about {chapter_data["name"]}?',
                    'option_a': 'Statement 1',
                    'option_b': 'Statement 2',
                    'option_c': 'Statement 3', 
                    'option_d': 'Statement 4',
                    'correct_option': 'B'
                }
            ]
            
            for i, q_data in enumerate(sample_questions):
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_data['question_text'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    correct_option=q_data['correct_option'],
                    marks=1,
                    order_index=i+1
                )
                db.session.add(question)
    
    db.session.commit()
    print("✅ Sample data created!")

if __name__ == '__main__':
    init_database()