from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Create a shared celery instance that can be imported by tasks
celery = Celery('quiz_master')

@celery.task
def export_user_data(user_id):
    """Export user data as CSV"""
    try:
        from models import User, QuizAttempt, db
        import csv
        import io
        from datetime import datetime
        
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
            
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Quiz ID', 'Quiz Title', 'Subject', 'Chapter', 
            'Date Taken', 'Score', 'Total Questions', 'Correct Answers',
            'Time Spent (minutes)', 'Status'
        ])
        
        # Write quiz attempts data
        attempts = QuizAttempt.query.filter_by(user_id=user_id, is_completed=True).all()
        for attempt in attempts:
            writer.writerow([
                attempt.quiz_id,
                attempt.quiz.title if attempt.quiz else 'N/A',
                attempt.quiz.chapter.subject.name if attempt.quiz and attempt.quiz.chapter else 'N/A',
                attempt.quiz.chapter.name if attempt.quiz and attempt.quiz.chapter else 'N/A',
                attempt.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.end_time else 'N/A',
                f"{attempt.score_percentage}%",
                attempt.total_questions,
                attempt.correct_answers,
                round((attempt.time_spent or 0) / 60, 2),
                'Completed' if attempt.is_completed else 'In Progress'
            ])
        
        # Send email with CSV attachment
        from extensions import mail
        from flask_mail import Message
        from config import Config
        
        msg = Message(
            'Your Quiz Data Export',
            sender=Config.MAIL_USERNAME,
            recipients=[user.email]
        )
        
        msg.body = f"""
Hi {user.full_name},

Your quiz data export is ready! Please find the CSV file attached.

This export contains data for {len(attempts)} completed quiz attempts.

Best regards,
QuizMaster Team
        """
        
        # Attach CSV file
        csv_content = output.getvalue()
        filename = f"quiz_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        msg.attach(filename, "text/csv", csv_content)
        
        mail.send(msg)
        
        return {
            'success': True,
            'message': f'Quiz data exported and sent to {user.email}',
            'records_exported': len(attempts)
        }
        
    except Exception as e:
        print(f"Error exporting user data: {e}")
        return {'success': False, 'message': str(e)}

@celery.task
def export_user_analytics_data(user_id, period='30d'):
    """Export user analytics data as CSV"""
    try:
        from models import User, QuizAttempt, db
        from datetime import datetime, timedelta
        import csv
        import io
        
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == '30d':
            start_date = end_date - timedelta(days=30)
        elif period == '60d':
            start_date = end_date - timedelta(days=60)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get user's quiz attempts for the period
        attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.timestamp_start >= start_date,
            QuizAttempt.is_completed == True
        ).order_by(QuizAttempt.timestamp_start.desc()).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Quiz Title', 'Subject', 'Chapter', 
            'Score', 'Max Score', 'Percentage', 'Time Taken (minutes)',
            'Questions Correct', 'Total Questions'
        ])
        
        # Write data
        for attempt in attempts:
            quiz = attempt.quiz
            chapter = quiz.chapter if quiz else None
            subject = chapter.subject if chapter else None
            
            time_taken = None
            if attempt.timestamp_end and attempt.timestamp_start:
                time_taken = (attempt.timestamp_end - attempt.timestamp_start).total_seconds() / 60
            
            percentage = round((attempt.score / attempt.max_score * 100), 2) if attempt.max_score > 0 else 0
            
            writer.writerow([
                attempt.timestamp_start.strftime('%Y-%m-%d'),
                quiz.title if quiz else 'N/A',
                subject.name if subject else 'N/A',
                chapter.name if chapter else 'N/A',
                attempt.score,
                attempt.max_score,
                percentage,
                round(time_taken, 2) if time_taken else 'N/A',
                attempt.score,  # Assuming score represents correct answers
                attempt.max_score
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Send email with attachment
        from extensions import mail
        from flask_mail import Message
        
        msg = Message(
            f"Quiz Master - Analytics Export ({period})",
            recipients=[user.email],
            body=f"Hi {user.full_name},\n\nYour analytics data export for {period} is ready.\n\nPlease find the attached CSV file.\n\nBest regards,\nQuiz Master Team"
        )
        
        filename = f"analytics_export_{user_id}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        msg.attach(filename, "text/csv", csv_content)
        
        mail.send(msg)
        
        return {
            'success': True,
            'message': f"Analytics data exported and sent to {user.email}",
            'records_exported': len(attempts)
        }
        
    except Exception as e:
        print(f"Error exporting analytics data: {e}")
        return {'success': False, 'message': str(e)}

@celery.task
def export_admin_data():
    """Export all users data for admin"""
    try:
        from models import User, QuizAttempt, db
        from datetime import datetime
        import csv
        import io
        
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            return {'success': False, 'message': 'Admin not found'}
        
        # Get all users and their quiz stats
        users = User.query.filter_by(role='user').all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'User ID', 'Username', 'Full Name', 'Email', 'Qualification',
            'Total Quizzes Taken', 'Average Score', 'Best Score', 
            'Last Quiz Date', 'Registration Date'
        ])
        
        # Write data
        for user in users:
            attempts = QuizAttempt.query.filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.is_completed == True
            ).all()
            
            total_quizzes = len(attempts)
            if total_quizzes > 0:
                scores = [attempt.score / attempt.max_score * 100 for attempt in attempts if attempt.max_score > 0]
                avg_score = sum(scores) / len(scores) if scores else 0
                best_score = max(scores) if scores else 0
                last_quiz_date = max([attempt.timestamp_start for attempt in attempts]).strftime('%Y-%m-%d')
            else:
                avg_score = 0
                best_score = 0
                last_quiz_date = 'Never'
            
            writer.writerow([
                user.id,
                user.email,
                user.full_name,
                user.email,
                user.qualification or 'Not specified',
                total_quizzes,
                round(avg_score, 2),
                round(best_score, 2),
                last_quiz_date,
                user.created_at.strftime('%Y-%m-%d') if user.created_at else 'Unknown'
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Send email with attachment
        from extensions import mail
        from flask_mail import Message
        
        msg = Message(
            "Quiz Master - Admin Data Export",
            recipients=[admin.email],
            body=f"Hi {admin.full_name},\n\nThe admin data export is ready. Please find the attached CSV file with all users' quiz statistics.\n\nBest regards,\nQuiz Master System"
        )
        
        filename = f"admin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        msg.attach(filename, "text/csv", csv_content)
        
        mail.send(msg)
        
        return {
            'success': True,
            'message': f"Admin data exported and sent to {admin.email}",
            'records_exported': len(users)
        }
        
    except Exception as e:
        print(f"Error exporting admin data: {e}")
        return {'success': False, 'message': str(e)}