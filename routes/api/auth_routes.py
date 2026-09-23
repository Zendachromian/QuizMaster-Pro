from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import api_bp
from models import User
from extensions import db, bcrypt
from datetime import datetime
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@api_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
            
        if not validate_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
            
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # Update last login and last visit
            user.last_login = datetime.utcnow()
            user.last_visit = datetime.utcnow()
            db.session.commit()
            
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'message': f'Login error: {str(e)}'}), 500

@api_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Validation
        if not all([email, password, full_name]):
            return jsonify({'message': 'All fields are required'}), 400
            
        if not validate_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
            
        is_valid, msg = validate_password(password)
        if not is_valid:
            return jsonify({'message': msg}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 400
            
        # Create user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User(
            email=email,
            username=email.split('@')[0],
            full_name=full_name,
            password=hashed_password,
            role='user'
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration error: {str(e)}'}), 500

@api_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        return jsonify({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': getattr(user, 'updated_at', None).isoformat() if getattr(user, 'updated_at', None) else None
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Profile error: {str(e)}'}), 500

@api_bp.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        data = request.get_json()
        full_name = data.get('full_name', '').strip()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        # Validation
        if not all([full_name, username, email]):
            return jsonify({'message': 'Full name, username, and email are required'}), 400
            
        if not validate_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
            
        # Check if email is taken by another user
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            return jsonify({'message': 'Email is already taken by another user'}), 400
            
        # Check if username is taken by another user
        existing_username = User.query.filter(User.username == username, User.id != user_id).first()
        if existing_username:
            return jsonify({'message': 'Username is already taken by another user'}), 400
        
        # Update basic info
        user.full_name = full_name
        user.username = username
        user.email = email
        
        # Handle password change
        if current_password and new_password:
            if not bcrypt.check_password_hash(user.password, current_password):
                return jsonify({'message': 'Current password is incorrect'}), 400
                
            is_valid, msg = validate_password(new_password)
            if not is_valid:
                return jsonify({'message': msg}), 400
                
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': getattr(user, 'updated_at', None).isoformat() if getattr(user, 'updated_at', None) else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Profile update error: {str(e)}'}), 500

@api_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # Get the JWT token identity
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user:
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
        
        # In a real app, you might want to blacklist the token
        # For now, we'll just return success and let frontend handle token removal
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout error: {str(e)}'
        }), 500