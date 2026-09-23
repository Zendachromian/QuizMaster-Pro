from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_bp
from models import User, Subject, Chapter, Quiz, Question, QuizAttempt
from extensions import db, cache
from datetime import datetime, timedelta
from sqlalchemy import func, desc, or_

def require_admin():
    """Check if current user is admin"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        return user and user.role == 'admin'
    except:
        return False

@api_bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Create cache key
        cache_key = "admin_dashboard_stats"
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return jsonify(cached_data)
        
        # Get dashboard statistics with error handling
        total_users = User.query.filter_by(role='user', is_active=True).count()
        total_subjects = Subject.query.filter_by(is_active=True).count()
        total_chapters = Chapter.query.filter_by(is_active=True).count()
        total_quizzes = Quiz.query.filter_by(is_active=True).count()
        total_attempts = QuizAttempt.query.filter_by(is_completed=True).count()
        
        stats = {
            'total_users': total_users,
            'total_subjects': total_subjects,
            'total_chapters': total_chapters,
            'total_quizzes': total_quizzes,
            'total_attempts': total_attempts
        }
        
        # Chart data calculations with fallbacks for empty database
        
        # User registration trend (last 7 days)
        user_registration_data = {'labels': [], 'data': []}
        for i in range(6, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            user_registration_data['labels'].append(date.strftime('%m/%d'))
            
            count = User.query.filter(
                func.date(User.created_at) == date
            ).count()
            user_registration_data['data'].append(count)
        
        # GitHub-style activity data (last 12 weeks)
        activity_data = {'weeks': [], 'data': []}
        today = datetime.now().date()
        
        # Start from 12 weeks ago, Sunday
        start_date = today - timedelta(days=today.weekday() + 1 + 77)  # 77 days = 11 weeks
        if start_date.weekday() != 6:  # If not Sunday, go to previous Sunday
            start_date = start_date - timedelta(days=start_date.weekday() + 1)
        
        current_date = start_date
        week_data = []
        
        for week in range(12):
            week_info = []
            for day in range(7):  # Sunday to Saturday
                date_str = current_date.strftime('%Y-%m-%d')
                
                # Count quiz attempts for this day
                attempt_count = QuizAttempt.query.filter(
                    func.date(QuizAttempt.start_time) == current_date
                ).count()
                
                day_data = {
                    'date': date_str,
                    'count': attempt_count,
                    'day': current_date.weekday(),  # 0=Monday, 6=Sunday
                    'week': week
                }
                week_info.append(day_data)
                current_date += timedelta(days=1)
            
            activity_data['weeks'].append(week_info)
        
        # Flatten for easier frontend processing
        activity_data['data'] = [day for week in activity_data['weeks'] for day in week]
        
        # Completion rates
        total_attempts_all = QuizAttempt.query.count()
        completed_attempts = QuizAttempt.query.filter(
            QuizAttempt.end_time.isnot(None)
        ).count()
        incomplete_attempts = total_attempts_all - completed_attempts
        
        completion_data = {
            'labels': ['Completed', 'Incomplete'],
            'data': [completed_attempts, incomplete_attempts if incomplete_attempts > 0 else 0]
        }
        
        # Subject popularity (simplified approach)
        subject_popularity_data = {'labels': [], 'data': []}
        try:
            # Get all subjects and count their quiz attempts
            subjects = Subject.query.filter_by(is_active=True).all()
            subject_attempts = []
            
            for subject in subjects:
                attempt_count = 0
                for chapter in subject.chapters.filter_by(is_active=True):
                    for quiz in chapter.quizzes.filter_by(is_active=True):
                        attempt_count += quiz.attempts.count()
                
                if attempt_count > 0:
                    subject_attempts.append((subject.name, attempt_count))
            
            # Sort by attempt count and take top 5
            subject_attempts.sort(key=lambda x: x[1], reverse=True)
            for subject_name, attempt_count in subject_attempts[:5]:
                subject_popularity_data['labels'].append(subject_name)
                subject_popularity_data['data'].append(attempt_count)
                
        except Exception as e:
            print(f"Error in subject popularity calculation: {e}")
        
        # Fallback: show top 5 subjects by quiz count
        if not subject_popularity_data['labels']:
            try:
                subjects = Subject.query.filter_by(is_active=True).limit(5).all()
                for subject in subjects:
                    quiz_count = 0
                    for chapter in subject.chapters.filter_by(is_active=True):
                        quiz_count += chapter.quizzes.filter_by(is_active=True).count()
                    
                    subject_popularity_data['labels'].append(subject.name)
                    subject_popularity_data['data'].append(quiz_count)
            except Exception as e:
                print(f"Error in fallback subject data: {e}")
        
        # Score distribution (5 ranges)
        score_distribution_data = {
            'labels': ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%'],
            'data': [0, 0, 0, 0, 0]
        }
        
        if total_attempts > 0:
            attempts = QuizAttempt.query.filter(
                QuizAttempt.score_percentage.isnot(None)
            ).all()
            
            for attempt in attempts:
                score = attempt.score_percentage
                if score <= 20:
                    score_distribution_data['data'][0] += 1
                elif score <= 40:
                    score_distribution_data['data'][1] += 1
                elif score <= 60:
                    score_distribution_data['data'][2] += 1
                elif score <= 80:
                    score_distribution_data['data'][3] += 1
                else:
                    score_distribution_data['data'][4] += 1
        
        # Qualifications distribution
        qualifications_data = {'labels': [], 'data': []}
        try:
            # Get all users with qualifications
            users_with_qualifications = User.query.filter(
                User.role == 'user',
                User.qualification.isnot(None),
                User.qualification != ''
            ).all()
            
            qualification_counts = {}
            for user in users_with_qualifications:
                qualification = user.qualification.strip()
                if qualification:
                    if qualification in qualification_counts:
                        qualification_counts[qualification] += 1
                    else:
                        qualification_counts[qualification] = 1
            
            # Sort by count and take top 8
            sorted_qualifications = sorted(qualification_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            
            for qualification, count in sorted_qualifications:
                qualifications_data['labels'].append(qualification)
                qualifications_data['data'].append(count)
                
            # If no qualifications found, show default message
            if not qualifications_data['labels']:
                qualifications_data['labels'] = ['No Data']
                qualifications_data['data'] = [0]
                
        except Exception as e:
            print(f"Error in qualifications calculation: {e}")
            qualifications_data = {'labels': ['No Data'], 'data': [0]}

        # Pass/Fail qualifications (separate from user qualifications)
        passed = QuizAttempt.query.filter(
            QuizAttempt.score_percentage >= 60
        ).count()
        failed = QuizAttempt.query.filter(
            QuizAttempt.score_percentage < 60
        ).count()
        
        quiz_qualifications_data = {
            'labels': ['Passed', 'Failed'],
            'data': [passed, failed]
        }
        
        # Subject performance (simplified approach)
        subject_performance_data = {'labels': [], 'scores': [], 'pass_rates': []}
        try:
            subjects = Subject.query.filter_by(is_active=True).limit(5).all()
            
            for subject in subjects:
                all_attempts = []
                
                # Collect all attempts for this subject
                for chapter in subject.chapters.filter_by(is_active=True):
                    for quiz in chapter.quizzes.filter_by(is_active=True):
                        attempts = quiz.attempts.filter_by(is_completed=True).all()
                        all_attempts.extend(attempts)
                
                if all_attempts:
                    # Calculate average score
                    avg_score = sum(attempt.score_percentage for attempt in all_attempts) / len(all_attempts)
                    
                    # Calculate pass rate
                    passed = sum(1 for attempt in all_attempts if attempt.score_percentage >= 60)
                    pass_rate = (passed / len(all_attempts)) * 100
                    
                    subject_performance_data['labels'].append(subject.name)
                    subject_performance_data['scores'].append(round(avg_score, 1))
                    subject_performance_data['pass_rates'].append(round(pass_rate, 1))
                else:
                    # No attempts yet, show 0 data
                    subject_performance_data['labels'].append(subject.name)
                    subject_performance_data['scores'].append(0)
                    subject_performance_data['pass_rates'].append(0)
                    
        except Exception as e:
            print(f"Error in subject performance calculation: {e}")
        
        # Fallback: show subjects with default values
        if not subject_performance_data['labels']:
            subjects = Subject.query.limit(5).all()
            for subject in subjects:
                subject_performance_data['labels'].append(subject.name)
                subject_performance_data['scores'].append(0)
                subject_performance_data['pass_rates'].append(0)
        
        # Performance metrics (calculated from existing data)
        performance_metrics_data = {
            'labels': ['Speed', 'Accuracy', 'Consistency', 'Improvement', 'Engagement'],
            'data': [0, 0, 0, 0, 0]
        }
        
        if total_attempts > 0:
            # Calculate some basic metrics
            avg_score = db.session.query(func.avg(QuizAttempt.score_percentage)).scalar() or 0
            performance_metrics_data['data'] = [
                round(avg_score * 0.8, 1),  # Speed (proxy)
                round(avg_score, 1),        # Accuracy
                round(avg_score * 0.9, 1),  # Consistency (proxy)
                round(avg_score * 0.7, 1),  # Improvement (proxy)
                round(completed_attempts / total_attempts_all * 100, 1)  # Engagement
            ]

        # Prepare chart data for frontend
        chart_data = {
            'user_registration': user_registration_data,
            'activity': activity_data,
            'completion_rates': completion_data,
            'subject_popularity': subject_popularity_data,
            'score_distribution': score_distribution_data,
            'qualifications': qualifications_data,
            'quiz_qualifications': quiz_qualifications_data,
            'subject_performance': subject_performance_data,
            'performance_metrics': performance_metrics_data
        }

        # Get recent attempts for dashboard (simplified)
        recent_attempts = QuizAttempt.query.filter(
            QuizAttempt.is_completed == True
        ).order_by(QuizAttempt.end_time.desc()).limit(10).all()

        recent_attempts_data = []
        for attempt in recent_attempts:
            recent_attempts_data.append({
                'id': attempt.id,
                'user': {
                    'full_name': attempt.user.full_name if attempt.user else None,
                    'email': attempt.user.email if attempt.user else None
                },
                'quiz_title': attempt.quiz.title,
                'subject_name': attempt.quiz.chapter.subject.name,
                'score_percentage': round(attempt.score_percentage, 1),
                'end_time': attempt.end_time.isoformat() if attempt.end_time else None
            })

        # Get recent users
        recent_users = User.query.filter_by(role='user').order_by(User.created_at.desc()).limit(10).all()

        recent_users_data = []
        for user in recent_users:
            recent_users_data.append({
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            })

        response_data = {
            'success': True,
            'stats': stats,
            'chart_data': chart_data,
            'recent_attempts': recent_attempts_data,
            'recent_users': recent_users_data
        }
        
        # Cache the result for 10 minutes
        cache.set(cache_key, response_data, timeout=600)

        return jsonify(response_data)

    except Exception as e:
        print(f"Dashboard error: {e}")
        return jsonify({'error': f'Dashboard error: {str(e)}'}), 500



# SUBJECT MANAGEMENT
@api_bp.route('/admin/subjects', methods=['GET'])
@jwt_required()
def admin_subjects():
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        subjects_query = Subject.query.filter_by(is_active=True).order_by(Subject.name)
        subjects = subjects_query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Safe serialization of subjects
        subjects_data = []
        for subject in subjects.items:
            try:
                subject_dict = {
                    'id': subject.id,
                    'name': subject.name,
                    'description': subject.description,
                    'created_at': subject.created_at.isoformat(),
                    'updated_at': subject.updated_at.isoformat(),
                    'is_active': subject.is_active,
                    'total_chapters': subject.chapters.filter_by(is_active=True).count(),
                    'total_quizzes': 0  # Will calculate safely
                }
                
                # Calculate total quizzes safely
                total_quizzes = 0
                for chapter in subject.chapters.filter_by(is_active=True):
                    total_quizzes += chapter.quizzes.filter_by(is_active=True).count()
                subject_dict['total_quizzes'] = total_quizzes
                
                subjects_data.append(subject_dict)
            except Exception as e:
                print(f"Error serializing subject {subject.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'subjects': subjects_data,
            'pagination': {
                'page': subjects.page,
                'pages': subjects.pages,
                'per_page': subjects.per_page,
                'total': subjects.total
            }
        })
        
    except Exception as e:
        print(f"Subjects error: {e}")
        return jsonify({'error': f'Error fetching subjects: {str(e)}'}), 500

@api_bp.route('/admin/subjects/create', methods=['POST'])
@jwt_required()
def create_subject():
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # Validation
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'error': 'Subject name is required'}), 400
        
        # Check if subject already exists
        if Subject.query.filter_by(name=name).first():
            return jsonify({'error': 'Subject with this name already exists'}), 400
        
        subject = Subject(
            name=name,
            description=description
        )
        
        db.session.add(subject)
        db.session.commit()
        cache.delete('subjects_list')
        
        return jsonify({
            'success': True,
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating subject: {str(e)}")
        return jsonify({'error': f'Error creating subject: {str(e)}'}), 500

@api_bp.route('/admin/subjects/<int:subject_id>/edit', methods=['PUT'])
@jwt_required()
def edit_subject(subject_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        subject = Subject.query.get_or_404(subject_id)
        data = request.get_json()
        
        # Validation
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'error': 'Subject name is required'}), 400
        
        # Check if another subject has this name
        existing = Subject.query.filter(Subject.name == name, Subject.id != subject_id).first()
        if existing:
            return jsonify({'error': 'Subject with this name already exists'}), 400
        
        subject.name = name
        subject.description = description
        subject.updated_at = datetime.utcnow()
        
        db.session.commit()
        cache.delete('subjects_list')
        
        return jsonify({
            'success': True,
            'message': 'Subject updated successfully',
            'subject': subject.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating subject: {str(e)}'}), 500

@api_bp.route('/admin/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
def delete_subject(subject_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        subject = Subject.query.get_or_404(subject_id)
        
        # Soft delete
        subject.is_active = False
        subject.updated_at = datetime.utcnow()
        
        db.session.commit()
        cache.delete('subjects_list')
        
        return jsonify({
            'success': True,
            'message': 'Subject deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting subject: {str(e)}'}), 500

@api_bp.route('/admin/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
def admin_subject_chapters(subject_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        subject = Subject.query.get_or_404(subject_id)
        chapters = Chapter.query.filter_by(subject_id=subject_id, is_active=True)\
            .order_by(Chapter.order_index, Chapter.name).all()
        
        return jsonify({
            'success': True,
            'subject': subject.to_dict(),
            'chapters': [chapter.to_dict() for chapter in chapters]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching chapters: {str(e)}'}), 500

@api_bp.route('/admin/subjects/<int:subject_id>/chapters/create', methods=['POST'])
@jwt_required()
def create_chapter(subject_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        order_index = data.get('order_index', 1)
        if not name:
            return jsonify({'error': 'Chapter name is required'}), 400
        # Check duplicate
        if Chapter.query.filter_by(subject_id=subject_id, name=name, is_active=True).first():
            return jsonify({'error': 'Chapter with this name already exists'}), 400
        chapter = Chapter(
            subject_id=subject_id,
            name=name,
            description=description,
            order_index=order_index
        )
        db.session.add(chapter)
        db.session.commit()
        cache.delete(f'chapters_{subject_id}')
        return jsonify({'success': True, 'message': 'Chapter created successfully', 'chapter': chapter.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating chapter: {str(e)}'}), 500

@api_bp.route('/admin/subjects/<int:subject_id>/chapters/<int:chapter_id>', methods=['PUT'])
@jwt_required()
def edit_chapter(subject_id, chapter_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        chapter = Chapter.query.filter_by(id=chapter_id, subject_id=subject_id, is_active=True).first_or_404()
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        order_index = data.get('order_index', chapter.order_index)
        if not name:
            return jsonify({'error': 'Chapter name is required'}), 400
        # Check duplicate
        if Chapter.query.filter(Chapter.subject_id==subject_id, Chapter.name==name, Chapter.id!=chapter_id, Chapter.is_active==True).first():
            return jsonify({'error': 'Chapter with this name already exists'}), 400
        chapter.name = name
        chapter.description = description
        chapter.order_index = order_index
        chapter.updated_at = datetime.utcnow()
        db.session.commit()
        cache.delete(f'chapters_{subject_id}')
        return jsonify({'success': True, 'message': 'Chapter updated successfully', 'chapter': chapter.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating chapter: {str(e)}'}), 500

@api_bp.route('/admin/subjects/<int:subject_id>/chapters/<int:chapter_id>', methods=['DELETE'])
@jwt_required()
def delete_chapter(subject_id, chapter_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        chapter = Chapter.query.filter_by(id=chapter_id, subject_id=subject_id).first_or_404()
        chapter.is_active = False
        chapter.updated_at = datetime.utcnow()
        db.session.commit()
        cache.delete(f'chapters_{subject_id}')
        return jsonify({'success': True, 'message': 'Chapter deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting chapter: {str(e)}'}), 500

# Quiz Management Endpoints
@api_bp.route('/admin/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
def admin_chapter_quizzes(chapter_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        chapter = Chapter.query.get_or_404(chapter_id)
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id, is_active=True)\
            .order_by(desc(Quiz.created_at)).all()
        
        return jsonify({
            'success': True,
            'chapter': chapter.to_dict(),
            'quizzes': [quiz.to_dict() for quiz in quizzes]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching quizzes: {str(e)}'}), 500

@api_bp.route('/admin/quizzes', methods=['GET'])
@jwt_required()
def admin_all_quizzes():
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get all quizzes with pagination
        quizzes_query = Quiz.query.filter_by(is_active=True)\
            .join(Chapter).join(Subject)\
            .order_by(desc(Quiz.created_at))
        
        quizzes = quizzes_query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Safe serialization of quizzes
        quizzes_data = []
        for quiz in quizzes.items:
            try:
                quizzes_data.append(quiz.to_dict())
            except Exception as e:
                print(f"Error serializing quiz {quiz.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'quizzes': quizzes_data,
            'pagination': {
                'page': quizzes.page,
                'pages': quizzes.pages,
                'per_page': quizzes.per_page,
                'total': quizzes.total
            }
        })
        
    except Exception as e:
        print(f"All quizzes error: {e}")
        return jsonify({'error': f'Error fetching quizzes: {str(e)}'}), 500

@api_bp.route('/admin/chapters/<int:chapter_id>/quizzes/create', methods=['POST'])
@jwt_required()
def create_quiz(chapter_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        date_of_quiz = data.get('date_of_quiz')
        time_duration = data.get('time_duration', 30)  # minutes
        max_attempts = data.get('max_attempts', 3)
        passing_score = data.get('passing_score', 60)
        
        if not title:
            return jsonify({'error': 'Quiz title is required'}), 400
        
        # Parse date
        quiz_date = None
        if date_of_quiz:
            try:
                quiz_date = datetime.fromisoformat(date_of_quiz.replace('Z', '+00:00'))
            except:
                return jsonify({'error': 'Invalid date format'}), 400
        
        quiz = Quiz(
            chapter_id=chapter_id,
            title=title,
            description=description,
            date_of_quiz=quiz_date or datetime.utcnow(),
            time_duration=time_duration,
            max_attempts=max_attempts,
            passing_score=passing_score
        )
        
        db.session.add(quiz)
        db.session.commit()
        cache.delete(f'quizzes_chapter_{chapter_id}')
        
        return jsonify({
            'success': True,
            'message': 'Quiz created successfully',
            'quiz': quiz.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating quiz: {str(e)}'}), 500

@api_bp.route('/admin/quizzes/<int:quiz_id>', methods=['PUT'])
@jwt_required()
def edit_quiz(quiz_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json() or {}
        
        quiz.title = data.get('title', quiz.title).strip()
        quiz.description = data.get('description', quiz.description)
        quiz.time_duration = data.get('time_duration', quiz.time_duration)
        quiz.max_attempts = data.get('max_attempts', quiz.max_attempts)
        quiz.passing_score = data.get('passing_score', quiz.passing_score)
        
        # Handle date update
        if data.get('date_of_quiz'):
            try:
                quiz.date_of_quiz = datetime.fromisoformat(data['date_of_quiz'].replace('Z', '+00:00'))
            except:
                return jsonify({'error': 'Invalid date format'}), 400
        
        quiz.updated_at = datetime.utcnow()
        db.session.commit()
        cache.delete(f'quizzes_chapter_{quiz.chapter_id}')
        
        return jsonify({
            'success': True,
            'message': 'Quiz updated successfully',
            'quiz': quiz.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating quiz: {str(e)}'}), 500

@api_bp.route('/admin/quizzes/<int:quiz_id>', methods=['DELETE'])
@jwt_required()
def delete_quiz(quiz_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz.is_active = False
        quiz.updated_at = datetime.utcnow()
        
        db.session.commit()
        cache.delete(f'quizzes_chapter_{quiz.chapter_id}')
        
        return jsonify({
            'success': True,
            'message': 'Quiz deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting quiz: {str(e)}'}), 500

# Question Management Endpoints
@api_bp.route('/admin/quizzes/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
def admin_quiz_questions(quiz_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id, is_active=True)\
            .order_by(Question.order_index).all()
        
        return jsonify({
            'success': True,
            'quiz': quiz.to_dict(),
            'questions': [question.to_dict(include_correct=True) for question in questions]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching questions: {str(e)}'}), 500

@api_bp.route('/admin/quizzes/<int:quiz_id>/questions/create', methods=['POST'])
@jwt_required()
def create_question(quiz_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json() or {}
        question_text = data.get('question_text', '').strip()
        option_a = data.get('option_a', '').strip()
        option_b = data.get('option_b', '').strip()
        option_c = data.get('option_c', '').strip()
        option_d = data.get('option_d', '').strip()
        correct_option = data.get('correct_option', '').upper()
        marks = data.get('marks', 1)
        order_index = data.get('order_index', 1)
        
        if not all([question_text, option_a, option_b, option_c, option_d, correct_option]):
            return jsonify({'error': 'All question fields are required'}), 400
        
        if correct_option not in ['A', 'B', 'C', 'D']:
            return jsonify({'error': 'Correct option must be A, B, C, or D'}), 400
        
        question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            marks=marks,
            order_index=order_index
        )
        
        db.session.add(question)
        db.session.commit()
        cache.delete(f'questions_quiz_{quiz_id}')
        
        return jsonify({
            'success': True,
            'message': 'Question created successfully',
            'question': question.to_dict(include_correct=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating question: {str(e)}'}), 500

@api_bp.route('/admin/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def edit_question(question_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        question = Question.query.get_or_404(question_id)
        data = request.get_json() or {}
        
        question.question_text = data.get('question_text', question.question_text).strip()
        question.option_a = data.get('option_a', question.option_a).strip()
        question.option_b = data.get('option_b', question.option_b).strip()
        question.option_c = data.get('option_c', question.option_c).strip()
        question.option_d = data.get('option_d', question.option_d).strip()
        
        correct_option = data.get('correct_option', question.correct_option).upper()
        if correct_option in ['A', 'B', 'C', 'D']:
            question.correct_option = correct_option
        
        question.marks = data.get('marks', question.marks)
        question.order_index = data.get('order_index', question.order_index)
        question.updated_at = datetime.utcnow()
        
        db.session.commit()
        cache.delete(f'questions_quiz_{question.quiz_id}')
        
        return jsonify({
            'success': True,
            'message': 'Question updated successfully',
            'question': question.to_dict(include_correct=True)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating question: {str(e)}'}), 500

@api_bp.route('/admin/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        question = Question.query.get_or_404(question_id)
        question.is_active = False
        question.updated_at = datetime.utcnow()
        
        db.session.commit()
        cache.delete(f'questions_quiz_{question.quiz_id}')
        
        return jsonify({
            'success': True,
            'message': 'Question deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting question: {str(e)}'}), 500

# Search Endpoints
@api_bp.route('/admin/search', methods=['GET'])
@jwt_required()
def admin_search():
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  # all, users, subjects, quizzes
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        results = {'users': [], 'subjects': [], 'quizzes': []}
        
        if search_type in ['all', 'users']:
            users = User.query.filter(
                User.role == 'user',
                User.is_active == True,
                db.or_(
                    User.full_name.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%'),
                    User.username.ilike(f'%{query}%')
                )
            ).limit(10).all()
            results['users'] = [user.to_dict() for user in users]
        
        if search_type in ['all', 'subjects']:
            subjects = Subject.query.filter(
                Subject.is_active == True,
                db.or_(
                    Subject.name.ilike(f'%{query}%'),
                    Subject.description.ilike(f'%{query}%')
                )
            ).limit(10).all()
            results['subjects'] = [subject.to_dict() for subject in subjects]
        
        if search_type in ['all', 'quizzes']:
            quizzes = Quiz.query.filter(
                Quiz.is_active == True,
                db.or_(
                    Quiz.title.ilike(f'%{query}%'),
                    Quiz.description.ilike(f'%{query}%')
                )
            ).join(Chapter).join(Subject).limit(10).all()
            results['quizzes'] = [quiz.to_dict() for quiz in quizzes]
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results['users']) + len(results['subjects']) + len(results['quizzes'])
        })
        
    except Exception as e:
        return jsonify({'error': f'Search error: {str(e)}'}), 500

@api_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def admin_users():
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        
        query = User.query.filter_by(role='user')
        
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.full_name.ilike(f'%{search}%')
                )
            )
        
        users = query.order_by(desc(User.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enhance user data with quiz performance
        users_data = []
        for user in users.items:
            user_dict = user.to_dict()
            
            # Get quiz attempts for this user
            completed_attempts = QuizAttempt.query.filter_by(
                user_id=user.id, 
                is_completed=True
            ).all()
            
            if completed_attempts:
                scores = [attempt.score_percentage for attempt in completed_attempts]
                user_dict['quiz_attempts'] = len(completed_attempts)
                user_dict['avg_score'] = round(sum(scores) / len(scores), 2)
                user_dict['best_score'] = max(scores)
                user_dict['last_attempt'] = max(attempt.end_time for attempt in completed_attempts).isoformat()
            else:
                user_dict['quiz_attempts'] = 0
                user_dict['avg_score'] = 0
                user_dict['best_score'] = 0
                user_dict['last_attempt'] = None
            
            users_data.append(user_dict)
        
        return jsonify({
            'success': True,
            'users': users_data,
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Users error: {str(e)}'}), 500

@api_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get_or_404(user_id)
        if user.role == 'admin':
            return jsonify({'error': 'Cannot modify admin users'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Status toggle error: {str(e)}'}), 500

@api_bp.route('/admin/users/<int:user_id>/edit', methods=['PUT'])
@jwt_required()
def edit_user(user_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get_or_404(user_id)
        if user.role == 'admin':
            return jsonify({'error': 'Cannot modify admin users'}), 400
        
        data = request.get_json()
        
        # Update user fields
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        if 'qualification' in data:
            user.qualification = data['qualification'].strip()
        if 'date_of_birth' in data and data['date_of_birth']:
            user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'User update error: {str(e)}'}), 500

@api_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get_or_404(user_id)
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin users'}), 400
        
        # Soft delete by setting is_active to False
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'User deletion error: {str(e)}'}), 500

@api_bp.route('/admin/export/users', methods=['GET'])
@jwt_required()
def export_users():
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        users = User.query.filter_by(role='user').all()
        
        export_data = []
        for user in users:
            attempts = QuizAttempt.query.filter_by(user_id=user.id, is_completed=True).all()
            
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'qualification': user.qualification,
                'created_at': user.created_at.isoformat(),
                'is_active': user.is_active,
                'total_attempts': len(attempts),
                'average_score': round(sum([a.score_percentage for a in attempts]) / len(attempts), 2) if attempts else 0
            }
            export_data.append(user_data)
        
        return jsonify({
            'success': True,
            'users': export_data,
            'total_users': len(export_data),
            'exported_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Export error: {str(e)}'}), 500

@api_bp.route('/admin/export/users', methods=['POST'])
@jwt_required()
def export_admin_data():
    try:
        # Check if user is admin
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Direct synchronous export for now (Celery not running)
        from datetime import datetime
        import csv
        import io
        
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
                scores = [attempt.score_percentage for attempt in attempts]
                avg_score = sum(scores) / len(scores) if scores else 0
                best_score = max(scores) if scores else 0
                last_quiz_date = max([attempt.start_time for attempt in attempts]).strftime('%Y-%m-%d')
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
        
        # Return CSV as download
        from flask import Response
        filename = f"admin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
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
