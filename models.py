from extensions import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    qualification = db.Column(db.String(200))
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_visit = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Notification settings
    reminder_enabled = db.Column(db.Boolean, default=True)
    reminder_time = db.Column(db.Integer, default=18)  # 6 PM
    email_notifications = db.Column(db.Boolean, default=True)
    monthly_report_enabled = db.Column(db.Boolean, default=True)
    monthly_report_format = db.Column(db.String(10), default='html')  # html or pdf
    
    # Relationships
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'qualification': self.qualification,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_visit': self.last_visit.isoformat() if self.last_visit else None,
            'is_active': self.is_active,
            'reminder_enabled': self.reminder_enabled,
            'reminder_time': self.reminder_time,
            'email_notifications': self.email_notifications,
            'monthly_report_enabled': self.monthly_report_enabled,
            'monthly_report_format': self.monthly_report_format
        }

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    chapters = db.relationship('Chapter', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    
    @hybrid_property
    def total_chapters(self):
        return self.chapters.filter_by(is_active=True).count()
    
    @hybrid_property
    def total_quizzes(self):
        return sum(chapter.total_quizzes for chapter in self.chapters.filter_by(is_active=True))
    
    def __repr__(self):
        return f'<Subject {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'total_chapters': self.total_chapters,
            'total_quizzes': self.total_quizzes
        }

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    
    @hybrid_property
    def total_quizzes(self):
        return self.quizzes.filter_by(is_active=True).count()
    
    def __repr__(self):
        return f'<Chapter {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name,
            'name': self.name,
            'description': self.description,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'total_quizzes': self.total_quizzes
        }

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)  # in minutes
    max_attempts = db.Column(db.Integer, default=3)
    passing_score = db.Column(db.Integer, default=60)  # percentage
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    
    @hybrid_property
    def total_questions(self):
        return self.questions.filter_by(is_active=True).count()
    
    @hybrid_property
    def total_attempts(self):
        return self.attempts.count()
    
    @hybrid_property
    def average_score(self):
        attempts = self.attempts.all()
        if not attempts:
            return 0
        return sum(attempt.score_percentage for attempt in attempts) / len(attempts)
    
    def __repr__(self):
        return f'<Quiz {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'chapter_name': self.chapter.name,
            'subject_name': self.chapter.subject.name,
            'title': self.title,
            'description': self.description,
            'date_of_quiz': self.date_of_quiz.isoformat(),
            'time_duration': self.time_duration,
            'max_attempts': self.max_attempts,
            'passing_score': self.passing_score,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'total_questions': self.total_questions,
            'total_attempts': self.total_attempts,
            'average_score': round(self.average_score, 2)
        }

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    explanation = db.Column(db.Text)
    marks = db.Column(db.Integer, default=1)
    order_index = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    answers = db.relationship('QuizAnswer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.id}>'
    
    def to_dict(self, include_correct=False):
        data = {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'explanation': self.explanation,
            'marks': self.marks,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
        
        if include_correct:
            data['correct_option'] = self.correct_option
            
        return data

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    unanswered = db.Column(db.Integer, default=0)
    total_marks = db.Column(db.Integer, default=0)
    obtained_marks = db.Column(db.Integer, default=0)
    score_percentage = db.Column(db.Float, default=0.0)
    time_taken = db.Column(db.Integer)  # in seconds
    is_completed = db.Column(db.Boolean, default=False)
    remarks = db.Column(db.Text)
    
    # Relationships
    answers = db.relationship('QuizAnswer', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')
    
    @hybrid_property
    def duration_formatted(self):
        if self.time_taken:
            hours = self.time_taken // 3600
            minutes = (self.time_taken % 3600) // 60
            seconds = self.time_taken % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"
    
    def __repr__(self):
        return f'<QuizAttempt {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz.title,
            'chapter_name': self.quiz.chapter.name,
            'subject_name': self.quiz.chapter.subject.name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'unanswered': self.unanswered,
            'total_marks': self.total_marks,
            'obtained_marks': self.obtained_marks,
            'score_percentage': self.score_percentage,
            'time_taken': self.time_taken,
            'duration_formatted': self.duration_formatted,
            'is_completed': self.is_completed,
            'remarks': self.remarks
        }

class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option = db.Column(db.String(1))  # A, B, C, D or None
    is_correct = db.Column(db.Boolean, default=False)
    marks_obtained = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer)  # in seconds
    
    def __repr__(self):
        return f'<QuizAnswer {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'question_id': self.question_id,
            'selected_option': self.selected_option,
            'is_correct': self.is_correct,
            'marks_obtained': self.marks_obtained,
            'time_taken': self.time_taken
        }