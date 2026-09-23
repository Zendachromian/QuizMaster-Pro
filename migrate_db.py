#!/usr/bin/env python
"""
Database migration script to add notification preferences and last_visit fields
"""
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append('/home/zendachromian/m2')

from init_app import create_app
from extensions import db
from models import User

def migrate_database():
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database migration...")
        
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            new_columns = ['last_visit', 'reminder_enabled', 'reminder_time', 'email_notifications', 'monthly_report_enabled']
            missing_columns = [col for col in new_columns if col not in columns]
            
            if not missing_columns:
                print("✅ All required columns already exist. Migration not needed.")
                return
            
            print(f"📋 Adding missing columns: {missing_columns}")
            
            # Add columns using raw SQL for better compatibility
            with db.engine.connect() as conn:
                trans = conn.begin()
                try:
                    for column in missing_columns:
                        if column == 'last_visit':
                            conn.execute(db.text("ALTER TABLE users ADD COLUMN last_visit DATETIME"))
                        elif column == 'reminder_enabled':
                            conn.execute(db.text("ALTER TABLE users ADD COLUMN reminder_enabled BOOLEAN DEFAULT 1"))
                        elif column == 'reminder_time':
                            conn.execute(db.text("ALTER TABLE users ADD COLUMN reminder_time INTEGER DEFAULT 18"))
                        elif column == 'email_notifications':
                            conn.execute(db.text("ALTER TABLE users ADD COLUMN email_notifications BOOLEAN DEFAULT 1"))
                        elif column == 'monthly_report_enabled':
                            conn.execute(db.text("ALTER TABLE users ADD COLUMN monthly_report_enabled BOOLEAN DEFAULT 1"))
                        
                        print(f"✓ Added column: {column}")
                    
                    trans.commit()
                    print("✅ Database migration completed successfully!")
                    
                except Exception as e:
                    trans.rollback()
                    print(f"❌ Migration failed: {e}")
                    raise
                    
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False
        
        return True

if __name__ == '__main__':
    migrate_database()
