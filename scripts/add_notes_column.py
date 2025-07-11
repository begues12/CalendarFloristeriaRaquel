#!/usr/bin/env python3
"""
Migration script to add can_manage_notes column to users table
"""

from app import create_app, db
from sqlalchemy import text, inspect
from app.models.user import User

def add_can_manage_notes_column():
    """Add can_manage_notes column to users table if it doesn't exist"""
    app = create_app()
    with app.app_context():
        
        # Check if column exists
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'can_manage_notes' in columns:
            print('ℹ️  Column can_manage_notes already exists')
            return
        
        try:
            # Add the column
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE users ADD COLUMN can_manage_notes BOOLEAN DEFAULT 1'))
                conn.commit()
            print('✅ Column can_manage_notes added to users table')
            
            # Update existing users to have the privilege
            with db.engine.connect() as conn:
                conn.execute(text('UPDATE users SET can_manage_notes = 1 WHERE can_manage_notes IS NULL'))
                conn.commit()
            print('✅ Existing users updated with can_manage_notes privilege')
            
        except Exception as e:
            print(f'❌ Error adding column: {e}')
            
            # If the above fails, try to recreate the table (last resort)
            print('🔄 Attempting to recreate tables...')
            try:
                # Create all tables (this will add missing columns)
                db.create_all()
                print('✅ Tables recreated successfully')
            except Exception as e2:
                print(f'❌ Error recreating tables: {e2}')

if __name__ == '__main__':
    add_can_manage_notes_column()
