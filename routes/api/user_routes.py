from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_bp
from models import User, Subject, Chapter, Quiz, Question, QuizAttempt, QuizAnswer
from extensions import db, cache
from datetime import datetime, timedelta
from sqlalchemy import desc, func
import random

@api_bp.route('/user/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user statistics
        attempts = QuizAttempt.query.filter_by(user_id=user_id, is_completed=True).all()
        subjects = Subject.query.filter_by(is_active=True).all()
        
        total_attempts = len(attempts)
        average_score = sum([attempt.score_percentage for attempt in attempts]) / total_attempts if total_attempts > 0 else 0
        best_score = max([attempt.score_percentage for attempt in attempts]) if attempts else 0
        
        stats = {
            'total_attempts': total_attempts,
            'average_score': round(average_score, 1),
            'best_score': best_score,
            'subjects_available': len(subjects)
        }
        
        # Get recent attempts (last 10)
        recent_attempts = QuizAttempt.query.filter_by(user_id=user_id, is_completed=True)\
            .order_by(desc(QuizAttempt.end_time))\
            .limit(10).all()
        
        # Get upcoming quizzes (next 7 days)
        upcoming_quizzes = Quiz.query.filter(
            Quiz.date_of_quiz >= datetime.utcnow(),
            Quiz.date_of_quiz <= datetime.utcnow() + timedelta(days=7),
            Quiz.is_active == True
        ).limit(5).all()
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'stats': stats,
            'recent_attempts': [attempt.to_dict() for attempt in recent_attempts],
            'subjects': [subject.to_dict() for subject in subjects[:6]],
            'upcoming_quizzes': [quiz.to_dict() for quiz in upcoming_quizzes]
        })
        
    except Exception as e:
        return f"Analytics data exported and sent to {user.email}"
    except Exception as e:
        return jsonify({'error': f'Export error: {str(e)}'}), 500

@api_bp.route('/user/notification-preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'preferences': {
                'reminder_enabled': user.reminder_enabled,
                'reminder_time': user.reminder_time,
                'email_notifications': user.email_notifications,
                'monthly_report_enabled': user.monthly_report_enabled,
                'monthly_report_format': user.monthly_report_format
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching preferences: {str(e)}'}), 500

@api_bp.route('/user/notification-preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update preferences
        if 'reminder_enabled' in data:
            user.reminder_enabled = bool(data['reminder_enabled'])
        if 'reminder_time' in data:
            reminder_time = int(data['reminder_time'])
            if 0 <= reminder_time <= 23:
                user.reminder_time = reminder_time
            else:
                return jsonify({'error': 'Reminder time must be between 0 and 23'}), 400
        if 'email_notifications' in data:
            user.email_notifications = bool(data['email_notifications'])
        if 'monthly_report_enabled' in data:
            user.monthly_report_enabled = bool(data['monthly_report_enabled'])
        if 'monthly_report_format' in data:
            if data['monthly_report_format'] in ['html', 'pdf']:
                user.monthly_report_format = data['monthly_report_format']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification preferences updated successfully',
            'preferences': {
                'reminder_enabled': user.reminder_enabled,
                'reminder_time': user.reminder_time,
                'email_notifications': user.email_notifications,
                'monthly_report_enabled': user.monthly_report_enabled,
                'monthly_report_format': user.monthly_report_format
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error updating preferences: {str(e)}'}), 500

@api_bp.route('/user/quizzes/search', methods=['GET'])
@jwt_required()
def search_quizzes():
    try:
        user_id = int(get_jwt_identity())
        
        # Get all active quizzes with their subject and chapter info
        quizzes = db.session.query(Quiz)\
            .join(Chapter)\
            .join(Subject)\
            .filter(Quiz.is_active == True)\
            .order_by(Quiz.title).all()
        
        # Get subjects for filter dropdown
        subjects = Subject.query.filter_by(is_active=True).order_by(Subject.name).all()
        
        # Enrich quiz data with user's attempts
        quiz_data = []
        for quiz in quizzes:
            quiz_dict = quiz.to_dict()
            
            # Add subject and chapter names
            quiz_dict['subject_name'] = quiz.chapter.subject.name
            quiz_dict['chapter_name'] = quiz.chapter.name
            quiz_dict['subject_id'] = quiz.chapter.subject.id
            
            # Get user's attempts for this quiz
            user_attempts = QuizAttempt.query.filter_by(
                user_id=user_id, 
                quiz_id=quiz.id, 
                is_completed=True
            ).order_by(desc(QuizAttempt.score_percentage)).all()
            
            # Check for ongoing attempt (not completed)
            ongoing_attempt = QuizAttempt.query.filter_by(
                user_id=user_id, 
                quiz_id=quiz.id, 
                is_completed=False
            ).first()
            
            quiz_dict['user_attempts'] = [attempt.to_dict() for attempt in user_attempts]
            quiz_dict['best_score'] = user_attempts[0].score_percentage if user_attempts else None
            quiz_dict['attempt_count'] = len(user_attempts)
            quiz_dict['ongoing_attempt'] = ongoing_attempt.to_dict() if ongoing_attempt else None
            
            # Determine quiz status
            current_time = datetime.utcnow()
            if ongoing_attempt:
                quiz_dict['status'] = 'ongoing'
                quiz_dict['status_message'] = f'Started on {ongoing_attempt.start_time.strftime("%Y-%m-%d %H:%M")}'
            elif quiz.date_of_quiz and quiz.date_of_quiz > current_time:
                quiz_dict['status'] = 'upcoming'
                quiz_dict['status_message'] = f'Available from {quiz.date_of_quiz.strftime("%Y-%m-%d %H:%M")}'
            elif user_attempts:
                quiz_dict['status'] = 'completed'
                last_attempt = max(user_attempts, key=lambda x: x.end_time)
                quiz_dict['status_message'] = f'Last completed on {last_attempt.end_time.strftime("%Y-%m-%d %H:%M")}'
            else:
                quiz_dict['status'] = 'available'
                quiz_dict['status_message'] = 'Ready to start'
            
            # Add total questions count
            quiz_dict['total_questions'] = Question.query.filter_by(
                quiz_id=quiz.id, 
                is_active=True
            ).count()
            
            quiz_data.append(quiz_dict)
        
        return jsonify({
            'success': True,
            'quizzes': quiz_data,
            'subjects': [subject.to_dict() for subject in subjects]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error searching quizzes: {str(e)}'}), 500

@api_bp.route('/user/subjects', methods=['GET'])
@jwt_required()
def subjects():
    try:
        user_id = int(get_jwt_identity())
        subjects = Subject.query.filter_by(is_active=True).order_by(Subject.name).all()
        
        subjects_data = []
        for subject in subjects:
            subject_dict = subject.to_dict()
            
            # Count chapters
            chapters_count = Chapter.query.filter_by(
                subject_id=subject.id, 
                is_active=True
            ).count()
            subject_dict['total_chapters'] = chapters_count
            
            # Count total quizzes in this subject
            total_quizzes = db.session.query(Quiz)\
                .join(Chapter)\
                .filter(Chapter.subject_id == subject.id, Quiz.is_active == True)\
                .count()
            subject_dict['total_quizzes'] = total_quizzes
            
            # Get user's attempts for this subject
            user_attempts = db.session.query(QuizAttempt)\
                .join(Quiz)\
                .join(Chapter)\
                .filter(
                    Chapter.subject_id == subject.id,
                    QuizAttempt.user_id == user_id,
                    QuizAttempt.is_completed == True
                ).all()
            
            subject_dict['user_attempts'] = len(user_attempts)
            
            # Calculate best score for this subject
            if user_attempts:
                best_score = max([attempt.score_percentage for attempt in user_attempts])
                subject_dict['best_score'] = best_score
                
                # Calculate progress (completed quizzes / total quizzes)
                completed_quizzes = len(set([attempt.quiz_id for attempt in user_attempts]))
                progress = (completed_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0
                subject_dict['user_progress'] = round(progress, 1)
            else:
                subject_dict['best_score'] = None
                subject_dict['user_progress'] = 0
            
            subjects_data.append(subject_dict)
        
        return jsonify({
            'success': True,
            'subjects': subjects_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching subjects: {str(e)}'}), 500

@api_bp.route('/user/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
def subject_chapters(subject_id):
    try:
        user_id = int(get_jwt_identity())
        subject = Subject.query.get_or_404(subject_id)
        chapters = Chapter.query.filter_by(subject_id=subject_id, is_active=True)\
            .order_by(Chapter.order_index, Chapter.name).all()
        
        # Enhance subject data
        subject_dict = subject.to_dict()
        
        # Count total quizzes and user attempts for this subject
        total_quizzes = db.session.query(Quiz)\
            .join(Chapter)\
            .filter(Chapter.subject_id == subject.id, Quiz.is_active == True)\
            .count()
        subject_dict['total_quizzes'] = total_quizzes
        
        user_attempts = db.session.query(QuizAttempt)\
            .join(Quiz)\
            .join(Chapter)\
            .filter(
                Chapter.subject_id == subject.id,
                QuizAttempt.user_id == user_id,
                QuizAttempt.is_completed == True
            ).all()
        
        subject_dict['user_attempts'] = len(user_attempts)
        
        if user_attempts:
            best_score = max([attempt.score_percentage for attempt in user_attempts])
            subject_dict['best_score'] = best_score
            
            completed_quizzes = len(set([attempt.quiz_id for attempt in user_attempts]))
            progress = (completed_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0
            subject_dict['user_progress'] = round(progress, 1)
        else:
            subject_dict['best_score'] = None
            subject_dict['user_progress'] = 0
        
        # Enhance chapters with quiz data
        chapters_data = []
        for chapter in chapters:
            chapter_dict = chapter.to_dict()
            
            # Get quizzes for this chapter
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id, is_active=True)\
                .order_by(Quiz.date_of_quiz.desc()).all()
            
            quizzes_data = []
            for quiz in quizzes:
                quiz_dict = quiz.to_dict()
                
                # Get question count
                quiz_dict['total_questions'] = Question.query.filter_by(
                    quiz_id=quiz.id, 
                    is_active=True
                ).count()
                
                # Get user's attempts for this quiz
                quiz_attempts = QuizAttempt.query.filter_by(
                    user_id=user_id, 
                    quiz_id=quiz.id, 
                    is_completed=True
                ).order_by(desc(QuizAttempt.score_percentage)).all()
                
                quiz_dict['attempts'] = [attempt.to_dict() for attempt in quiz_attempts]
                
                # Determine quiz status
                if quiz_attempts:
                    quiz_dict['status'] = 'completed'
                    quiz_dict['best_score'] = quiz_attempts[0].score_percentage
                else:
                    # Check if quiz is available (date-based)
                    if quiz.date_of_quiz <= datetime.utcnow():
                        quiz_dict['status'] = 'available'
                    else:
                        quiz_dict['status'] = 'locked'
                    quiz_dict['best_score'] = None
                
                quizzes_data.append(quiz_dict)
            
            chapter_dict['quizzes'] = quizzes_data
            
            # Calculate chapter completion
            if quizzes_data:
                completed_quizzes = len([q for q in quizzes_data if q['status'] == 'completed'])
                completion = (completed_quizzes / len(quizzes_data) * 100) if quizzes_data else 0
                chapter_dict['completion_percentage'] = round(completion, 1)
            else:
                chapter_dict['completion_percentage'] = 0
            
            chapters_data.append(chapter_dict)
        
        return jsonify({
            'success': True,
            'subject': subject_dict,
            'chapters': chapters_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching chapters: {str(e)}'}), 500

@api_bp.route('/user/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
def chapter_quizzes(chapter_id):
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id, is_active=True)\
            .order_by(Quiz.date_of_quiz.desc()).all()
        
        return jsonify({
            'success': True,
            'chapter': chapter.to_dict(),
            'quizzes': [quiz.to_dict() for quiz in quizzes]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching quizzes: {str(e)}'}), 500

@api_bp.route('/user/quiz/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    try:
        user_id = int(get_jwt_identity())
        quiz = Quiz.query.get_or_404(quiz_id)
        
        # Check if user has exceeded max attempts
        existing_attempts = QuizAttempt.query.filter_by(
            user_id=user_id, 
            quiz_id=quiz_id,
            is_completed=True
        ).count()
        
        if quiz.max_attempts and existing_attempts >= quiz.max_attempts:
            return jsonify({
                'success': False,
                'message': f'Maximum attempts ({quiz.max_attempts}) reached for this quiz'
            }), 400
        
        # Check if quiz is available
        if quiz.date_of_quiz and quiz.date_of_quiz > datetime.utcnow():
            return jsonify({
                'success': False,
                'message': 'Quiz is not yet available'
            }), 400
        
        # Get questions for the quiz
        questions = Question.query.filter_by(quiz_id=quiz_id, is_active=True)\
            .order_by(Question.order_index).all()
        
        if not questions:
            return jsonify({
                'success': False,
                'message': 'No questions available for this quiz'
            }), 400
        
        # Create quiz attempt
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            start_time=datetime.utcnow(),
            total_questions=len(questions),
            total_marks=sum([q.marks for q in questions])
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        # Return questions without correct answers
        questions_data = [q.to_dict(include_correct=False) for q in questions]
        
        return jsonify({
            'success': True,
            'quiz': quiz.to_dict(),
            'questions': questions_data,
            'attempt': attempt.to_dict(),
            'time_duration': quiz.time_duration
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error starting quiz: {str(e)}'
        }), 500

@api_bp.route('/user/attempt/<int:attempt_id>/save-answer', methods=['POST'])
@jwt_required()
def save_answer(attempt_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        attempt = QuizAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
        if not attempt:
            return jsonify({'error': 'Quiz attempt not found'}), 404
        
        if attempt.is_completed:
            return jsonify({'error': 'Quiz is already completed'}), 400
        
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        
        question = Question.query.get_or_404(question_id)
        
        # Check if answer already exists
        answer = QuizAnswer.query.filter_by(
            attempt_id=attempt_id,
            question_id=question_id
        ).first()
        
        if answer:
            # Update existing answer
            answer.selected_option = selected_option
            answer.is_correct = (selected_option == question.correct_option)
            answer.marks_obtained = question.marks if answer.is_correct else 0
        else:
            # Create new answer
            answer = QuizAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                selected_option=selected_option,
                is_correct=(selected_option == question.correct_option),
                marks_obtained=question.marks if (selected_option == question.correct_option) else 0
            )
            db.session.add(answer)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Answer saved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error saving answer: {str(e)}'}), 500

@api_bp.route('/user/attempt/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(attempt_id):
    try:
        user_id = int(get_jwt_identity())
        print(f"🚀 Submit quiz called for attempt {attempt_id} by user {user_id}")
        
        attempt = QuizAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
        if not attempt:
            print(f"❌ No attempt found for ID {attempt_id} and user {user_id}")
            return jsonify({'error': 'Quiz attempt not found'}), 404
        
        if attempt.is_completed:
            print(f"⚠️ Attempt {attempt_id} is already completed")
            return jsonify({'error': 'Quiz is already completed'}), 400
        
        print(f"📊 Processing attempt {attempt_id} for quiz {attempt.quiz_id}")
        
        # Calculate final score
        answers = QuizAnswer.query.filter_by(attempt_id=attempt_id).all()
        print(f"📝 Found {len(answers)} answers for attempt {attempt_id}")
        
        total_marks = 0
        obtained_marks = 0
        correct_answers = 0
        
        for answer in answers:
            total_marks += answer.question.marks
            obtained_marks += answer.marks_obtained
            if answer.is_correct:
                correct_answers += 1
        
        # Calculate percentage
        score_percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
        print(f"📈 Score calculated: {obtained_marks}/{total_marks} = {score_percentage}%")
        
        # Update attempt
        attempt.end_time = datetime.utcnow()
        attempt.is_completed = True
        attempt.total_marks = total_marks
        attempt.obtained_marks = obtained_marks
        attempt.score_percentage = round(score_percentage, 2)
        attempt.correct_answers = correct_answers
        attempt.total_questions = len(answers)
        
        # Calculate time spent
        if attempt.start_time:
            time_diff = attempt.end_time - attempt.start_time
            attempt.time_spent = int(time_diff.total_seconds())
        
        # Determine result based on passing score
        quiz = attempt.quiz
        attempt.result = 'Pass' if score_percentage >= quiz.passing_score else 'Fail'
        
        print(f"✅ Attempt {attempt_id} marked as completed with result: {attempt.result}")
        
        db.session.commit()
        print(f"💾 Database committed for attempt {attempt_id}")
        
        # Clear any cached data
        cache.delete(f'user_stats_{user_id}')
        
        return jsonify({
            'success': True,
            'message': 'Quiz submitted successfully',
            'result': {
                'score_percentage': attempt.score_percentage,
                'obtained_marks': obtained_marks,
                'total_marks': total_marks,
                'correct_answers': correct_answers,
                'total_questions': attempt.total_questions,
                'time_spent': attempt.time_spent,
                'result': attempt.result
            }
        })
        
    except Exception as e:
        print(f"💥 Error in submit_quiz: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Error submitting quiz: {str(e)}'}), 500

@api_bp.route('/user/quiz/<int:quiz_id>/result', methods=['GET'])
@jwt_required()  
def quiz_result(quiz_id):
    try:
        user_id = int(get_jwt_identity())
        
        # Get the latest completed attempt for this quiz
        attempt = QuizAttempt.query.filter_by(
            user_id=user_id, 
            quiz_id=quiz_id, 
            is_completed=True
        ).order_by(desc(QuizAttempt.end_time)).first()
        
        if not attempt:
            return jsonify({'error': 'No completed attempt found for this quiz'}), 404
        
        # Get detailed answers
        answers = QuizAnswer.query.filter_by(attempt_id=attempt.id)\
            .join(Question).all()
        
        answer_details = []
        for answer in answers:
            question = answer.question
            answer_details.append({
                'question_text': question.question_text,
                'options': {
                    'A': question.option_a,
                    'B': question.option_b,
                    'C': question.option_c,
                    'D': question.option_d
                },
                'selected_option': answer.selected_option,
                'correct_option': question.correct_option,
                'is_correct': answer.is_correct,
                'marks': question.marks,
                'marks_obtained': answer.marks_obtained
            })
        
        return jsonify({
            'success': True,
            'quiz': attempt.quiz.to_dict(),
            'attempt': attempt.to_dict(),
            'answers': answer_details
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching result: {str(e)}'}), 500

@api_bp.route('/user/history', methods=['GET'])
@jwt_required()
def quiz_history():
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        limit = request.args.get('limit', type=int)
        
        query = QuizAttempt.query.filter_by(user_id=user_id, is_completed=True)\
            .order_by(desc(QuizAttempt.end_time))
        
        if limit:
            attempts = query.limit(limit).all()
            return jsonify({
                'success': True,
                'attempts': [attempt.to_dict() for attempt in attempts]
            })
        else:
            attempts = query.paginate(page=page, per_page=per_page, error_out=False)
            return jsonify({
                'success': True,
                'attempts': [attempt.to_dict() for attempt in attempts.items],
                'pagination': {
                    'page': attempts.page,
                    'pages': attempts.pages,
                    'per_page': attempts.per_page,
                    'total': attempts.total
                }
            })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching history: {str(e)}'}), 500

@api_bp.route('/user/analytics', methods=['GET'])
@jwt_required()
def get_user_analytics():
    try:
        user_id = int(get_jwt_identity())
        period = request.args.get('period', '30d')
        
        # Create cache key
        cache_key = f"user_analytics_{user_id}_{period}"
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return jsonify(cached_data)
        
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == '30d':
            start_date = end_date - timedelta(days=30)
            days = 30
        elif period == '60d':
            start_date = end_date - timedelta(days=60)
            days = 60
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
            days = 90
        else:
            start_date = end_date - timedelta(days=30)
            days = 30

        # Get user's quiz attempts for the period
        attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.start_time >= start_date,
            QuizAttempt.is_completed == True
        ).all()

        # Calculate basic stats
        total_attempts = len(attempts)
        if total_attempts > 0:
            scores = [attempt.score_percentage for attempt in attempts]
            average_score = sum(scores) / len(scores) if scores else 0
            best_score = max(scores) if scores else 0
            
            # Calculate total time spent
            total_time = 0
            for attempt in attempts:
                if attempt.end_time and attempt.start_time:
                    time_diff = attempt.end_time - attempt.start_time
                    total_time += time_diff.total_seconds()
        else:
            average_score = 0
            best_score = 0
            total_time = 0

        # Create activity data for chart
        activity_data = []
        for i in range(days):
            date = (end_date - timedelta(days=days-1-i)).date()
            daily_attempts = len([a for a in attempts if a.start_time.date() == date])
            activity_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': daily_attempts
            })

        # Score distribution data
        score_ranges = [
            {'range': '90-100%', 'min': 90, 'max': 100},
            {'range': '80-89%', 'min': 80, 'max': 89},
            {'range': '70-79%', 'min': 70, 'max': 79},
            {'range': '60-69%', 'min': 60, 'max': 69},
            {'range': '50-59%', 'min': 50, 'max': 59},
            {'range': '<50%', 'min': 0, 'max': 49}
        ]
        
        score_distribution_data = []
        for score_range in score_ranges:
            count = len([a for a in attempts if 
                        score_range['min'] <= a.score_percentage <= score_range['max']])
            score_distribution_data.append({
                'range': score_range['range'],
                'count': count
            })

        # Subject performance data
        subject_performance = {}
        for attempt in attempts:
            if attempt.quiz and attempt.quiz.chapter and attempt.quiz.chapter.subject:
                subject_name = attempt.quiz.chapter.subject.name
                if subject_name not in subject_performance:
                    subject_performance[subject_name] = {
                        'attempts': 0,
                        'scores': [],
                        'time_spent': 0
                    }
                
                subject_performance[subject_name]['attempts'] += 1
                score_percentage = attempt.score_percentage
                subject_performance[subject_name]['scores'].append(score_percentage)
                
                if attempt.end_time and attempt.start_time:
                    time_diff = attempt.end_time - attempt.start_time
                    subject_performance[subject_name]['time_spent'] += time_diff.total_seconds()

        subject_performance_data = []
        for subject, data in subject_performance.items():
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            best_score = max(data['scores']) if data['scores'] else 0
            
            subject_performance_data.append({
                'subject': subject,
                'attempts': data['attempts'],
                'average_score': round(avg_score, 2),
                'best_score': round(best_score, 2),
                'time_spent': int(data['time_spent'])
            })

        # Monthly performance trend
        monthly_performance = {}
        for attempt in attempts:
            month_key = attempt.start_time.strftime('%Y-%m')
            if month_key not in monthly_performance:
                monthly_performance[month_key] = {
                    'attempts': 0,
                    'scores': []
                }
            
            monthly_performance[month_key]['attempts'] += 1
            score_percentage = attempt.score_percentage
            monthly_performance[month_key]['scores'].append(score_percentage)

        monthly_performance_data = []
        for month, data in sorted(monthly_performance.items()):
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            
            # Format month for display
            month_obj = datetime.strptime(month, '%Y-%m')
            month_display = month_obj.strftime('%b %Y')
            
            monthly_performance_data.append({
                'month': month_display,
                'attempts': data['attempts'],
                'average_score': round(avg_score, 2)
            })

        # Prepare response data
        response_data = {
            'stats': {
                'total_attempts': total_attempts,
                'average_score': round(average_score, 2),
                'best_score': round(best_score, 2),
                'total_time_spent': int(total_time)
            },
            'chartData': {
                'activity': {
                    'data': activity_data
                },
                'score_distribution': {
                    'data': score_distribution_data
                },
                'subject_performance': {
                    'data': subject_performance_data
                },
                'monthly_performance': {
                    'data': monthly_performance_data
                }
            },
            'performance': subject_performance_data
        }
        
        # Cache the result for 5 minutes
        cache.set(cache_key, response_data, timeout=300)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Error fetching analytics: {str(e)}'}), 500

@api_bp.route('/user/quiz-status', methods=['GET'])
@jwt_required()
def get_quiz_status():
    """Get quiz status data for charts - attempted, not attempted, and upcoming quizzes"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get all active quizzes
        all_quizzes = Quiz.query.filter_by(is_active=True).all()
        
        # Get user's completed attempts
        user_attempts = QuizAttempt.query.filter_by(
            user_id=user_id, 
            is_completed=True
        ).all()
        
        # Get quiz IDs that user has attempted
        attempted_quiz_ids = set(attempt.quiz_id for attempt in user_attempts)
        
        # Current date for comparison
        current_date = datetime.utcnow()
        
        # Categorize quizzes
        attempted_quizzes = []
        not_attempted_quizzes = []
        upcoming_quizzes = []
        
        for quiz in all_quizzes:
            if quiz.id in attempted_quiz_ids:
                attempted_quizzes.append(quiz)
            elif quiz.date_of_quiz > current_date:
                upcoming_quizzes.append(quiz)
            else:
                not_attempted_quizzes.append(quiz)
        
        # Prepare chart data
        chart_data = {
            'attempted': {
                'count': len(attempted_quizzes),
                'quizzes': [{'id': q.id, 'title': q.title, 'subject': q.chapter.subject.name, 'date': q.date_of_quiz.isoformat()} for q in attempted_quizzes[:10]]
            },
            'not_attempted': {
                'count': len(not_attempted_quizzes),
                'quizzes': [{'id': q.id, 'title': q.title, 'subject': q.chapter.subject.name, 'date': q.date_of_quiz.isoformat()} for q in not_attempted_quizzes[:10]]
            },
            'upcoming': {
                'count': len(upcoming_quizzes),
                'quizzes': [{'id': q.id, 'title': q.title, 'subject': q.chapter.subject.name, 'date': q.date_of_quiz.isoformat()} for q in upcoming_quizzes[:10]]
            }
        }
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching quiz status: {str(e)}'}), 500

@api_bp.route('/user/export-data', methods=['POST'])
@jwt_required()
def export_user_data():
    try:
        user_id = int(get_jwt_identity())
        
        # Direct synchronous export for now (Celery not running)
        from models import User, QuizAttempt
        from datetime import datetime
        import csv
        import io
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Quiz ID', 'Quiz Title', 'Subject', 'Chapter', 
            'Date Taken', 'Score', 'Max Score', 'Percentage',
            'Time Spent (minutes)', 'Status'
        ])
        
        # Write quiz attempts data
        attempts = QuizAttempt.query.filter_by(user_id=user_id, is_completed=True).all()
        for attempt in attempts:
            quiz = attempt.quiz
            chapter = quiz.chapter if quiz else None
            subject = chapter.subject if chapter else None
            
            time_taken = None
            if attempt.end_time and attempt.start_time:
                time_taken = (attempt.end_time - attempt.start_time).total_seconds() / 60
            
            percentage = round(attempt.score_percentage, 2)
            
            writer.writerow([
                attempt.quiz_id,
                quiz.title if quiz else 'N/A',
                subject.name if subject else 'N/A',
                chapter.name if chapter else 'N/A',
                attempt.start_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.start_time else 'N/A',
                attempt.obtained_marks,
                attempt.total_marks,
                f"{percentage}%",
                round(time_taken, 2) if time_taken else 'N/A',
                'Completed' if attempt.is_completed else 'In Progress'
            ])
        
        # Return CSV as download
        csv_content = output.getvalue()
        output.close()
        
        # Create response with CSV content
        from flask import Response
        filename = f"quiz_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
    except Exception as e:
        return jsonify({'error': f'Export error: {str(e)}'}), 500

@api_bp.route('/user/export-analytics', methods=['POST'])
@jwt_required()
def export_user_analytics():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        period = data.get('period', '30d')
        
        # Direct synchronous export for now (Celery not running)
        from models import User, QuizAttempt
        from datetime import datetime, timedelta
        import csv
        import io
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
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
            QuizAttempt.start_time >= start_date,
            QuizAttempt.is_completed == True
        ).order_by(QuizAttempt.start_time.desc()).all()
        
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
            if attempt.end_time and attempt.start_time:
                time_taken = (attempt.end_time - attempt.start_time).total_seconds() / 60
            
            percentage = round(attempt.score_percentage, 2)
            
            writer.writerow([
                attempt.start_time.strftime('%Y-%m-%d'),
                quiz.title if quiz else 'N/A',
                subject.name if subject else 'N/A',
                chapter.name if chapter else 'N/A',
                attempt.obtained_marks,
                attempt.total_marks,
                percentage,
                round(time_taken, 2) if time_taken else 'N/A',
                attempt.correct_answers,  # Correct answers count
                attempt.total_questions
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Return CSV as download
        from flask import Response
        filename = f"analytics_export_{user_id}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
    except Exception as e:
        return jsonify({'error': f'Export error: {str(e)}'}), 500
