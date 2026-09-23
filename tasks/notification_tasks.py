from datetime import datetime, timedelta
from sqlalchemy import func
import requests
from models import User, Quiz, QuizAttempt
from extensions import db, mail
from flask_mail import Message
from config import Config
from utils.pdf_generator import generate_monthly_report_pdf

# Import the celery instance from the main tasks module
from . import celery

@celery.task
def send_daily_reminders():
    """Send daily reminders to inactive users"""
    try:
        # Find users who haven't taken a quiz in the last 3 days
        cutoff_date = datetime.utcnow() - timedelta(days=3)
        
        inactive_users = db.session.query(User).filter(
            User.role == 'user',
            User.is_active == True,
            ~User.id.in_(
                db.session.query(QuizAttempt.user_id).filter(
                    QuizAttempt.start_time > cutoff_date
                )
            )
        ).all()
        
        # Check for new quizzes created in the last day
        yesterday = datetime.utcnow() - timedelta(days=1)
        new_quizzes = Quiz.query.filter(
            Quiz.created_at > yesterday,
            Quiz.is_active == True
        ).all()
        
        reminder_count = 0
        
        for user in inactive_users:
            # Check if user has relevant new quizzes
            relevant_quizzes = []
            for quiz in new_quizzes:
                # You can add logic here to determine relevance based on user preferences
                relevant_quizzes.append(quiz)
            
            if len(relevant_quizzes) > 0 or True:  # Send reminder anyway
                # Send email reminder
                try:
                    msg = Message(
                        'Quiz Reminder - New quizzes available!',
                        sender=Config.MAIL_USERNAME,
                        recipients=[user.email]
                    )
                    
                    msg.html = f"""
                    <h2>Hi {user.full_name}!</h2>
                    <p>We noticed you haven't taken any quizzes recently. Come back and test your knowledge!</p>
                    
                    {'<h3>New quizzes available:</h3><ul>' + ''.join([f'<li>{quiz.title}</li>' for quiz in relevant_quizzes]) + '</ul>' if relevant_quizzes else ''}
                    
                    <p><a href="{Config.APP_URL}/login" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login and Start Quiz</a></p>
                    
                    <p>Best regards,<br>QuizMaster Team</p>
                    """
                    
                    mail.send(msg)
                    reminder_count += 1
                    
                except Exception as e:
                    print(f"Failed to send reminder to {user.email}: {e}")
                
                # Send Google Chat notification (if webhook URL is configured)
                try:
                    webhook_url = getattr(Config, 'GOOGLE_CHAT_WEBHOOK_URL', None)
                    if webhook_url:
                        message = {
                            "text": f"📚 Reminder: {user.full_name}, you have pending quizzes to attempt!"
                        }
                        requests.post(webhook_url, json=message)
                except Exception as e:
                    print(f"Failed to send chat notification: {e}")
        
        return {
            'success': True,
            'reminders_sent': reminder_count,
            'message': f'Sent {reminder_count} daily reminders'
        }
        
    except Exception as e:
        print(f"Error in send_daily_reminders: {e}")
        return {
            'success': False,
            'message': str(e)
        }

@celery.task
def generate_monthly_report():
    """Generate monthly activity reports for all users"""
    try:
        # Get all active users
        users = User.query.filter_by(role='user', is_active=True).all()
        
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
                QuizAttempt.is_completed == True,
                QuizAttempt.end_time >= first_day_last_month,
                QuizAttempt.end_time <= last_day_last_month
            ).all()
            
            if not attempts:
                continue  # Skip users with no activity
            
            # Calculate statistics
            total_attempts = len(attempts)
            scores = [attempt.score_percentage for attempt in attempts]
            average_score = sum(scores) / len(scores)
            best_score = max(scores)
            worst_score = min(scores)
            
            # Calculate time spent
            total_time = sum([attempt.time_spent or 0 for attempt in attempts])
            avg_time_per_quiz = total_time / total_attempts if total_attempts > 0 else 0
            
            # Subject-wise performance
            subject_stats = {}
            for attempt in attempts:
                if attempt.quiz and attempt.quiz.chapter:
                    subject_name = attempt.quiz.chapter.subject.name
                    if subject_name not in subject_stats:
                        subject_stats[subject_name] = []
                    subject_stats[subject_name].append(attempt.score_percentage)
            
            # Calculate ranking (simplified - just percentage above average)
            all_scores_this_month = db.session.query(QuizAttempt.score_percentage).filter(
                QuizAttempt.is_completed == True,
                QuizAttempt.end_time >= first_day_last_month,
                QuizAttempt.end_time <= last_day_last_month
            ).all()
            
            avg_all_users = sum([score[0] for score in all_scores_this_month]) / len(all_scores_this_month) if all_scores_this_month else 0
            performance_rating = "Above Average" if average_score > avg_all_users else "Below Average"
            
            # Generate HTML report
            html_report = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Monthly Quiz Report - {last_day_last_month.strftime('%B %Y')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .stat-card {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
                    .subject-performance {{ margin: 20px 0; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Monthly Quiz Report</h1>
                    <h2>{last_day_last_month.strftime('%B %Y')}</h2>
                    <p>Hi {user.full_name}!</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>{total_attempts}</h3>
                        <p>Quizzes Taken</p>
                    </div>
                    <div class="stat-card">
                        <h3>{average_score:.1f}%</h3>
                        <p>Average Score</p>
                    </div>
                    <div class="stat-card">
                        <h3>{best_score:.1f}%</h3>
                        <p>Best Score</p>
                    </div>
                    <div class="stat-card">
                        <h3>{avg_time_per_quiz/60:.1f} min</h3>
                        <p>Avg Time per Quiz</p>
                    </div>
                </div>
                
                <div class="subject-performance">
                    <h3>Subject-wise Performance</h3>
                    <table>
                        <tr>
                            <th>Subject</th>
                            <th>Quizzes Taken</th>
                            <th>Average Score</th>
                            <th>Best Score</th>
                        </tr>
            """
            
            for subject, scores in subject_stats.items():
                html_report += f"""
                        <tr>
                            <td>{subject}</td>
                            <td>{len(scores)}</td>
                            <td>{sum(scores)/len(scores):.1f}%</td>
                            <td>{max(scores):.1f}%</td>
                        </tr>
                """
            
            html_report += f"""
                    </table>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; background-color: #e7f3ff; border-radius: 5px;">
                    <h3>Performance Rating: {performance_rating}</h3>
                    <p>Keep up the great work! Continue learning and improving your scores.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{Config.APP_URL}/login" style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Take More Quizzes</a>
                </div>
                
                <p style="text-align: center; color: #666; margin-top: 30px;">
                    Best regards,<br>
                    QuizMaster Team
                </p>
            </body>
            </html>
            """
            
            # Send email with report
            try:
                # Prepare report data for PDF generation
                report_data = {
                    'month_year': last_day_last_month.strftime('%B %Y'),
                    'total_attempts': total_attempts,
                    'average_score': average_score,
                    'best_score': best_score,
                    'avg_time_per_quiz': avg_time_per_quiz,
                    'subject_stats': subject_stats,
                    'performance_rating': performance_rating
                }
                
                user_data = {
                    'full_name': user.full_name,
                    'email': user.email
                }
                
                msg = Message(
                    f'Your Monthly Quiz Report - {last_day_last_month.strftime("%B %Y")}',
                    sender=Config.MAIL_USERNAME,
                    recipients=[user.email]
                )
                
                # Check user's preferred format
                if hasattr(user, 'monthly_report_format') and user.monthly_report_format == 'pdf':
                    # Generate PDF report
                    pdf_content = generate_monthly_report_pdf(user_data, report_data)
                    
                    # Create a simple text email body for PDF
                    msg.body = f"""
Hi {user.full_name}!

Your monthly quiz report for {last_day_last_month.strftime('%B %Y')} is ready!

Please find your detailed performance report attached as a PDF.

Key highlights:
- Quizzes Completed: {total_attempts}
- Average Score: {average_score:.1f}%
- Best Score: {best_score:.1f}%

Keep up the great work!

Best regards,
QuizMaster Team
                    """
                    
                    # Attach PDF
                    filename = f"monthly_report_{user.id}_{last_day_last_month.strftime('%Y_%m')}.pdf"
                    msg.attach(filename, "application/pdf", pdf_content)
                    
                else:
                    # Use HTML format (default)
                    msg.html = html_report
                
                mail.send(msg)
                reports_sent += 1
                
            except Exception as e:
                print(f"Failed to send monthly report to {user.email}: {e}")
        
        return {
            'success': True,
            'reports_sent': reports_sent,
            'message': f'Sent {reports_sent} monthly reports'
        }
        
    except Exception as e:
        print(f"Error in generate_monthly_report: {e}")
        return {
            'success': False,
            'message': str(e)
        }

@celery.task
def export_user_quiz_data(user_id):
    """Export user's quiz data as CSV and send via email"""
    try:
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        # Get user's quiz attempts
        attempts = QuizAttempt.query.filter_by(user_id=user_id, is_completed=True)\
            .order_by(QuizAttempt.end_time.desc()).all()
        
        if not attempts:
            return {'success': False, 'message': 'No quiz data found for this user'}
        
        # Create CSV data
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Quiz ID', 'Quiz Title', 'Subject', 'Chapter', 'Date Taken',
            'Time Taken (mins)', 'Total Questions', 'Correct Answers',
            'Wrong Answers', 'Score Percentage', 'Result'
        ])
        
        # Write data rows
        for attempt in attempts:
            quiz = attempt.quiz
            chapter = quiz.chapter if quiz else None
            subject = chapter.subject if chapter else None
            
            writer.writerow([
                attempt.quiz_id,
                quiz.title if quiz else 'N/A',
                subject.name if subject else 'N/A',
                chapter.name if chapter else 'N/A',
                attempt.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.end_time else 'N/A',
                round((attempt.time_spent or 0) / 60, 2),
                attempt.total_questions,
                attempt.correct_answers,
                attempt.total_questions - attempt.correct_answers,
                f"{attempt.score_percentage}%",
                'Pass' if attempt.score_percentage >= 60 else 'Fail'
            ])
        
        # Save CSV content
        csv_content = output.getvalue()
        
        # Send email with CSV attachment
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
        msg.attach(
            f"quiz_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            csv_content
        )
        
        mail.send(msg)
        
        return {
            'success': True,
            'message': f'Quiz data exported and sent to {user.email}',
            'records_exported': len(attempts)
        }
        
    except Exception as e:
        print(f"Error in export_user_quiz_data: {e}")
        return {
            'success': False,
            'message': str(e)
        }