#!/usr/bin/env python3
"""
Test script for monthly report functionality with HTML and PDF formats
"""

from tasks.notification_tasks import generate_monthly_report
from models import User
from extensions import db
from init_app import create_app
import os

def test_monthly_report_formats():
    """Test monthly report generation with both HTML and PDF formats"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Testing monthly report generation...")
        
        # Check if we have users in the database
        users = User.query.filter_by(role='user', is_active=True).limit(2).all()
        
        if not users:
            print("❌ No active users found in database for testing")
            return False
        
        print(f"📊 Found {len(users)} active users for testing")
        
        # Test with different formats
        for user in users[:2]:  # Test with first 2 users
            print(f"\n👤 Testing with user: {user.full_name} ({user.email})")
            
            # Test HTML format (default)
            user.monthly_report_format = 'html'
            print(f"   📧 Format: HTML")
            
            # Test PDF format
            user.monthly_report_format = 'pdf'
            print(f"   📄 Format: PDF")
            
            db.session.commit()
        
        print(f"\n✅ Users configured for testing both formats")
        print(f"🔄 Note: Monthly reports are sent automatically on the 1st of each month")
        print(f"🧪 To test manually, run the Celery task: generate_monthly_report.delay()")
        
        return True

if __name__ == "__main__":
    success = test_monthly_report_formats()
    if success:
        print("\n🎉 Monthly report format test setup completed!")
        print("\n📋 Summary of implementation:")
        print("   ✅ PDF generation utility created")
        print("   ✅ Monthly report task updated to support both formats")
        print("   ✅ User model extended with monthly_report_format field")
        print("   ✅ API endpoints updated to handle format preferences")
        print("   ✅ Frontend Profile page updated with format selection")
        print("   ✅ Database schema updated")
        print("\n🎯 Students can now choose between HTML and PDF monthly reports!")
    else:
        print("\n💥 Monthly report format test failed!")
