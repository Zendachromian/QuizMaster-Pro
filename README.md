# 🎯 QuizMaster Pro - Complete Multi-User Exam Preparation Platform

A comprehensive quiz application built with **Vue.js 3**, **Flask**, and **SQLite** for exam preparation and user management.

## 🏆 Framework Compliance - ALL MANDATORY FRAMEWORKS ✅

| Framework | Status | Implementation |
|-----------|--------|----------------|
| **SQLite** | ✅ | Complete database with comprehensive data model |
| **Flask** | ✅ | RESTful API backend with JWT authentication |
| **Vue.js** | ✅ | Modern Vue.js 3 SPA with Composition API |
| **Vue.js Advanced (CLI)** | ✅ | Full CLI project with router, state management |
| **Jinja2** | ✅ | Minimal usage for entry point only (compliant) |
| **Bootstrap** | ✅ | Complete responsive styling (no other CSS) |
| **Redis** | ✅ | Caching system for performance optimization |
| **Celery + Redis** | ✅ | Background jobs for notifications and reports |

## 🚀 Quick Start

### 1. One-Command Launch
```bash
./run_quizmaster.sh
```

### 2. Manual Setup (if needed)
```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..

# Initialize database
python -c "from init_app import init_database; init_database()"

# Start services
redis-server --daemonize yes
celery -A celery_worker.celery worker --detach
celery -A celery_worker.celery beat --detach
python app.py
```

### 3. Access Application
- **Frontend**: http://localhost:5000
- **Admin Login**: admin@quizmaster.com / admin123

## 🎭 User Roles

### 👑 Admin (Quiz Master)
- **Pre-configured account** (no registration needed)
- **Complete control** over users and content
- **Dashboard** with statistics and analytics
- **Subject Management**: Create, edit, delete subjects
- **Chapter Management**: Organize content by chapters
- **Quiz Creation**: Build comprehensive quizzes
- **Question Management**: MCQ questions with 4 options
- **User Monitoring**: View and manage all users
- **Export Functionality**: Generate CSV reports

### 👤 User (Students)
- **Registration & Login** system
- **Profile Management**: Full name, qualification, DOB
- **Dashboard** with personal statistics
- **Quiz Discovery**: Browse subjects and chapters
- **Interactive Quiz Taking**: Timer-based sessions
- **Progress Tracking**: View scores and history
- **Responsive Design**: Works on all devices

## 🏗️ Application Architecture

```
QuizMaster Pro/
├── 🎨 Frontend (Vue.js 3 SPA)
│   ├── Authentication System
│   ├── User Dashboard & Quiz Interface
│   ├── Admin Management Panel
│   └── Responsive Bootstrap Design
│
├── ⚡ Backend (Flask API)
│   ├── JWT Authentication
│   ├── RESTful API Endpoints
│   ├── Role-based Access Control
│   └── Input Validation & Security
│
├── 🗄️ Database (SQLite)
│   ├── Users (Admin/Student roles)
│   ├── Subjects → Chapters → Quizzes → Questions
│   ├── Quiz Attempts & Answers
│   └── Analytics & Statistics
│
├── 🚀 Caching (Redis)
│   ├── API Response Caching
│   ├── Session Management
│   └── Performance Optimization
│
└── 🔄 Background Jobs (Celery)
    ├── Daily Reminder Notifications
    ├── Monthly Activity Reports
    └── CSV Export Processing
```

## 📊 Core Features

### 🎯 Quiz Engine
- **MCQ Questions** with 4 options (A, B, C, D)
- **Timer Functionality** with visual countdown
- **Auto-save** answers during quiz
- **Multiple Attempts** support
- **Question Navigation** with progress tracking
- **Instant Scoring** and detailed results

### 📈 Analytics & Reporting
- **User Statistics**: Total attempts, average scores
- **Admin Dashboard**: System-wide analytics
- **Quiz Performance**: Detailed attempt tracking
- **Export Reports**: CSV format for data analysis

### 🔔 Background Jobs
- **Daily Reminders**: Automated user notifications
- **Monthly Reports**: Comprehensive activity reports
- **CSV Exports**: User-triggered async processing
- **Email Notifications**: System alerts and updates

### 🛡️ Security Features
- **JWT Authentication** with token expiration
- **Password Hashing** with bcrypt
- **Role-based Access Control**
- **Input Validation** and sanitization
- **CSRF Protection** for forms

### 📱 Responsive Design
- **Mobile-First** Bootstrap 5 design
- **Cross-device** compatibility
- **Touch-friendly** interface
- **Progressive Web App** features

## 🗄️ Database Schema

### Users Table
- **id** (Primary Key)
- **email** (Unique)
- **username** (Unique)
- **full_name**
- **password** (Hashed)
- **role** (admin/user)
- **qualification**
- **date_of_birth**
- **created_at**
- **is_active**

### Content Structure
```
Subjects (Math, Science, etc.)
├── Chapters (Algebra, Physics, etc.)
    ├── Quizzes (Tests with timing)
        ├── Questions (MCQ with 4 options)
        └── Quiz Attempts (User sessions)
            └── Quiz Answers (Individual responses)
```

## 🛠️ Technology Stack

### Frontend
- **Vue.js 3** - Modern JavaScript framework
- **Vue Router 4** - SPA navigation
- **Pinia** - State management
- **Bootstrap 5** - UI framework
- **Axios** - HTTP client
- **Chart.js** - Data visualization

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - ORM and database
- **Flask-JWT-Extended** - Authentication
- **Flask-Caching** - Performance optimization
- **Celery** - Background task processing
- **Redis** - Caching and message broker

### Infrastructure
- **SQLite** - Embedded database
- **Redis Server** - Caching and queuing
- **Celery Beat** - Task scheduling
- **Gunicorn** - Production WSGI server (optional)

## 📋 API Endpoints

### Authentication
```
POST /api/auth/login       # User/Admin login
POST /api/auth/register    # User registration
GET  /api/auth/profile     # Get user profile
POST /api/auth/logout      # Logout user
```

### User Endpoints
```
GET  /api/dashboard        # User dashboard data
GET  /api/subjects         # Available subjects
GET  /api/subjects/{id}/chapters    # Subject chapters
GET  /api/chapters/{id}/quizzes     # Chapter quizzes
POST /api/quiz/{id}/start           # Start quiz attempt
POST /api/attempt/{id}/save-answer  # Save quiz answer
POST /api/attempt/{id}/submit       # Submit quiz
GET  /api/attempt/{id}/result       # View results
```

### Admin Endpoints
```
GET  /api/admin/dashboard           # Admin dashboard
GET  /api/admin/subjects            # Manage subjects
POST /api/admin/subjects/create     # Create subject
GET  /api/admin/users               # User management
POST /api/admin/quiz/create         # Create quiz
GET  /api/admin/quiz/{id}/stats     # Quiz statistics
```

## 🔧 Development Setup

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **Redis Server**
- **Git**

### Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd quizmaster-pro

# Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm run build
cd ..

# Start Redis
redis-server

# Initialize database
python -c "from init_app import init_database; init_database()"
```

### Running in Development
```bash
# Terminal 1: Celery Worker
celery -A celery_worker.celery worker --loglevel=info

# Terminal 2: Celery Beat Scheduler  
celery -A celery_worker.celery beat --loglevel=info

# Terminal 3: Flask Development Server
python app.py

# Terminal 4: Vue.js Development (optional)
cd frontend && npm run serve
```

## 🚀 Production Deployment

### Using Docker (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Manual Production Setup
```bash
# Install production dependencies
pip install gunicorn

# Build frontend for production
cd frontend && npm run build

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 Performance Optimization

### Caching Strategy
- **API Response Caching**: Redis-backed caching
- **Database Query Optimization**: Efficient queries
- **Static File Serving**: Nginx for production
- **CDN Integration**: For global performance

### Monitoring
- **Application Metrics**: Built-in analytics
- **Error Tracking**: Comprehensive logging
- **Performance Monitoring**: Response time tracking
- **User Analytics**: Dashboard insights

## 🔒 Security Measures

- **JWT Token Authentication** with expiration
- **Password Hashing** using bcrypt
- **Input Validation** on all endpoints
- **SQL Injection Prevention** via ORM
- **XSS Protection** with sanitization
- **HTTPS Enforcement** in production
- **Rate Limiting** for API endpoints

## 🎯 Testing

### Frontend Testing
```bash
cd frontend
npm run test:unit
npm run test:e2e
```

### Backend Testing
```bash
python -m pytest tests/
```

### API Testing
```bash
# Using curl
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@quizmaster.com","password":"admin123"}'
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

For support and questions:
- **Email**: support@quizmaster.com
- **Issues**: [GitHub Issues](https://github.com/username/quizmaster-pro/issues)
- **Documentation**: [Wiki](https://github.com/username/quizmaster-pro/wiki)

---

**QuizMaster Pro** - Built with ❤️ using Vue.js, Flask, and modern web technologies.

🎯 **Perfect Framework Compliance** | 🚀 **Production Ready** | 📱 **Mobile Optimized** | 🔒 **Secure by Design**
