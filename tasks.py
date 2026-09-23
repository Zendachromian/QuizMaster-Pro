import os
import csv
import io
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab
from flask import current_app, render_template_string
from flask_mail import Message
from extensions import db, mail, cache
from models import User, Quiz, QuizAttempt, Subject, Chapter
import requests
import json

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

# This will be initialized in app.py
celery = Celery('quiz_master')

@celery.task
def send_daily_reminder():
    """Send daily reminders to inactive users."""
    try:
        # Find users who haven't visited or attempted any quiz in the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Get users who:
        # 1. Have reminders enabled
        # 2. Haven't visited in the last 24 hours OR haven't attempted any quiz recently
        # 3. Are active users (not admin)
        inactive_users = db.session.query(User).filter(
            User.reminder_enabled == True,
            User.role == 'user',
            User.is_active == True,
            db.or_(
                User.last_visit < yesterday,
                User.last_visit.is_(None),
                ~User.id.in_(
                    db.session.query(QuizAttempt.user_id).filter(
                        QuizAttempt.timestamp_start >= yesterday
                    )
                )
            )
        ).all()
        
        # Get new quizzes created in the last 24 hours
        new_quizzes = Quiz.query.filter(
            Quiz.created_at >= yesterday,
            Quiz.is_active == True
        ).all()
        
        reminders_sent = 0
        for user in inactive_users:
            # Check if there are relevant new quizzes for this user
            relevant_quizzes = []
            for quiz in new_quizzes:
                # You can add logic here to check if quiz is relevant to user's interests
                # For now, we'll include all new quizzes
                relevant_quizzes.append(quiz)
            
            # Send reminder if user hasn't visited recently or there are new quizzes
            should_send_reminder = (
                not user.last_visit or user.last_visit < yesterday or 
                len(relevant_quizzes) > 0
            )
            
            if should_send_reminder:
                send_reminder_notification.delay(user.id, len(relevant_quizzes))
                reminders_sent += 1
        
        return f"Sent reminders to {reminders_sent} users ({len(new_quizzes)} new quizzes available)"
    except Exception as e:
        return f"Error sending reminders: {str(e)}"

@celery.task
def send_reminder_notification(user_id, new_quiz_count):
    """Send reminder notification via email or webhook."""
    try:
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        # Try to send via Google Chat webhook (if configured)
        webhook_url = current_app.config.get('GOOGLE_CHAT_WEBHOOK_URL')
        if webhook_url:
            message = {
                "text": f"🎯 Hi {user.full_name}! You have {new_quiz_count} new quizzes waiting. Visit Quiz Master to test your knowledge!"
            }
            response = requests.post(webhook_url, json=message)
        
        # Fallback to email
        msg = Message(
            subject="Quiz Master - Daily Reminder",
            recipients=[user.email],
            html=render_template_string('''
            <h2>Quiz Master Daily Reminder</h2>
            <p>Hi {{ name }},</p>
            <p>You haven't visited Quiz Master recently. We have {{ quiz_count }} new quizzes that might interest you!</p>
            <p><a href="{{ app_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Take Quiz Now</a></p>
            <p>Keep learning!</p>
            ''', name=user.full_name, quiz_count=new_quiz_count, app_url=current_app.config.get('APP_URL', 'http://localhost:5000'))
        )
        mail.send(msg)
        
        return f"Reminder sent to {user.email}"
    except Exception as e:
        return f"Error: {str(e)}"

@celery.task
def generate_monthly_report():
    """Generate and send monthly activity reports to all users."""
    try:
        # Get all users who have monthly reports enabled
        users = User.query.filter_by(
            role='user',
            is_active=True,
            monthly_report_enabled=True
        ).all()
        
        # Calculate date range for last month
        today = datetime.utcnow()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        
        reports_sent = 0
        
        for user in users:
            # Get user's quiz attempts for last month
            attempts = QuizAttempt.query.filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.timestamp_start >= first_day_last_month,
                QuizAttempt.timestamp_start <= last_day_last_month,
                QuizAttempt.is_completed == True
            ).all()
            
            # Only send report if user has some activity
            if attempts:
                # Generate report data
                total_quizzes = len(attempts)
                total_score = sum([attempt.score for attempt in attempts])
                average_score = total_score / total_quizzes if total_quizzes > 0 else 0
                
                # Calculate ranking (simplified)
                all_scores = [attempt.score for attempt in attempts]
                all_scores.sort(reverse=True)
                user_best_score = max(all_scores) if all_scores else 0
                
                # Send monthly report
                send_monthly_report_email.delay(user.id, {
                    'total_quizzes': total_quizzes,
                    'average_score': round(average_score, 2),
                    'best_score': user_best_score,
                    'month_year': last_day_last_month.strftime('%B %Y')
                })
                reports_sent += 1
        
        return f"Monthly reports queued for {reports_sent} users"
    except Exception as e:
        return f"Error generating monthly reports: {str(e)}"

@celery.task
def send_monthly_report_email(user_id, report_data):
    """Send monthly report email to user."""
    try:
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        html_content = render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Monthly Quiz Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #007bff; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .stats { display: flex; justify-content: space-around; margin: 20px 0; }
                .stat-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
                .footer { background-color: #6c757d; color: white; padding: 10px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Quiz Master Monthly Report</h1>
                <p>{{ month_year }}</p>
            </div>
            <div class="content">
                <h2>Hi {{ name }}!</h2>
                <p>Here's your quiz performance summary for {{ month_year }}:</p>
                
                <div class="stats">
                    <div class="stat-box">
                        <h3>{{ total_quizzes }}</h3>
                        <p>Quizzes Completed</p>
                    </div>
                    <div class="stat-box">
                        <h3>{{ average_score }}%</h3>
                        <p>Average Score</p>
                    </div>
                    <div class="stat-box">
                        <h3>{{ best_score }}%</h3>
                        <p>Best Score</p>
                    </div>
                </div>
                
                <p>Keep up the great work! Continue learning and improving your knowledge.</p>
                <p><a href="{{ app_url }}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Take More Quizzes</a></p>
            </div>
            <div class="footer">
                <p>Quiz Master &copy; 2025</p>
            </div>
        </body>
        </html>
        ''', 
        name=user.full_name, 
        month_year=report_data['month_year'],
        total_quizzes=report_data['total_quizzes'],
        average_score=report_data['average_score'],
        best_score=report_data['best_score'],
        app_url=current_app.config.get('APP_URL', 'http://localhost:5000')
        )
        
        msg = Message(
            subject=f"Quiz Master Monthly Report - {report_data['month_year']}",
            recipients=[user.email],
            html=html_content
        )
        mail.send(msg)
        
        return f"Monthly report sent to {user.email}"
    except Exception as e:
        return f"Error sending monthly report: {str(e)}"

@celery.task
def export_user_quiz_data(user_id):
    """Export user's quiz data to CSV."""
    try:
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        # Get user's quiz attempts
        attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_completed == True
        ).order_by(QuizAttempt.timestamp_start.desc()).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Quiz ID', 'Quiz Title', 'Subject', 'Chapter', 
            'Date Attempted', 'Score', 'Max Score', 'Percentage',
            'Time Taken (minutes)', 'Remarks'
        ])
        
        # Write data
        for attempt in attempts:
            quiz = attempt.quiz
            chapter = quiz.chapter
            subject = chapter.subject
            
            time_taken = None
            if attempt.timestamp_end and attempt.timestamp_start:
                time_taken = (attempt.timestamp_end - attempt.timestamp_start).total_seconds() / 60
            
            writer.writerow([
                quiz.id,
                quiz.title,
                subject.name,
                chapter.name,
                attempt.timestamp_start.strftime('%Y-%m-%d %H:%M'),
                attempt.score,
                attempt.max_score,
                round((attempt.score / attempt.max_score * 100), 2) if attempt.max_score > 0 else 0,
                round(time_taken, 2) if time_taken else 'N/A',
                quiz.remarks or 'No remarks'
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Save to file
        filename = f"quiz_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'w', newline='') as f:
            f.write(csv_content)
        
        # Send email with attachment
        msg = Message(
            subject="Quiz Master - Your Quiz Data Export",
            recipients=[user.email],
            body=f"Hi {user.full_name},\n\nYour quiz data export is ready. Please find the attached CSV file.\n\nBest regards,\nQuiz Master Team"
        )
        
        with open(filepath, 'r') as f:
            msg.attach(filename, "text/csv", f.read())
        
        mail.send(msg)
        
        # Clean up file
        os.remove(filepath)
        
        return f"Quiz data exported and sent to {user.email}"
    except Exception as e:
        return f"Error exporting quiz data: {str(e)}"

@celery.task
def export_admin_data():
    """Export all users' quiz data for admin."""
    try:
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            return "Admin not found"
        
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
        
        # Save to file
        filename = f"admin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'w', newline='') as f:
            f.write(csv_content)
        
        # Send email with attachment
        msg = Message(
            subject="Quiz Master - Admin Data Export",
            recipients=[admin.email],
            body=f"Hi {admin.full_name},\n\nThe admin data export is ready. Please find the attached CSV file with all users' quiz statistics.\n\nBest regards,\nQuiz Master System"
        )
        
        with open(filepath, 'r') as f:
            msg.attach(filename, "text/csv", f.read())
        
        mail.send(msg)
        
        # Clean up file
        os.remove(filepath)
        
        return f"Admin data exported and sent to {admin.email}"
    except Exception as e:
        return f"Error exporting admin data: {str(e)}"

@celery.task
def export_user_analytics_data(user_id, period='30d'):
    """Export user's analytics data to CSV."""
    try:
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
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
            chapter = quiz.chapter
            subject = chapter.subject
            
            time_taken = None
            if attempt.timestamp_end and attempt.timestamp_start:
                time_taken = (attempt.timestamp_end - attempt.timestamp_start).total_seconds() / 60
            
            percentage = round((attempt.score / attempt.max_score * 100), 2) if attempt.max_score > 0 else 0
            
            writer.writerow([
                attempt.timestamp_start.strftime('%Y-%m-%d'),
                quiz.title,
                subject.name,
                chapter.name,
                attempt.score,
                attempt.max_score,
                percentage,
                round(time_taken, 2) if time_taken else 'N/A',
                attempt.score,  # Assuming score represents correct answers
                attempt.max_score
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Create analytics summary
        if attempts:
            total_attempts = len(attempts)
            total_score = sum([attempt.score for attempt in attempts])
            avg_score = total_score / total_attempts if total_attempts > 0 else 0
            max_score_possible = sum([attempt.max_score for attempt in attempts])
            overall_percentage = (total_score / max_score_possible * 100) if max_score_possible > 0 else 0
            
            summary_content = f"""
Analytics Summary for {period}:
- Total Quiz Attempts: {total_attempts}
- Average Score: {avg_score:.2f}
- Overall Percentage: {overall_percentage:.2f}%
- Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
            """
        else:
            summary_content = f"No quiz attempts found for the selected period ({period})."
        
        # Save to file
        filename = f"analytics_export_{user_id}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'w', newline='') as f:
            f.write(csv_content)
        
        # Send email with attachment
        msg = Message(
            subject=f"Quiz Master - Analytics Export ({period})",
            recipients=[user.email],
            body=f"Hi {user.full_name},\n\nYour analytics data export for {period} is ready.\n\n{summary_content}\n\nPlease find the attached CSV file.\n\nBest regards,\nQuiz Master Team"
        )
        
        with open(filepath, 'r') as f:
            msg.attach(filename, "text/csv", f.read())
        
        mail.send(msg)
        
        # Clean up file
        os.remove(filepath)
        
        return f"Analytics data exported and sent to {user.email}"
    except Exception as e:
        return f"Error exporting analytics data: {str(e)}"