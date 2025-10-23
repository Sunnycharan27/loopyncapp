"""
Google Sheets Database Module for User Authentication
This module handles all CRUD operations for user data stored in Google Sheets.
For DEMO/TEST purposes, it includes a mock mode that simulates Google Sheets operations.
"""

import os
import uuid
import bcrypt
from datetime import datetime, timezone
from typing import Optional, Dict, List
import json

# Try to import gspread, but allow for demo mode if not configured
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    print("Warning: gspread not available. Running in demo mode.")


class SheetsDB:
    """
    Google Sheets Database for user authentication.
    Supports both real Google Sheets and demo/mock mode.
    """
    
    def __init__(self, demo_mode=True):
        """
        Initialize the Google Sheets database connection.
        
        Args:
            demo_mode: If True, uses in-memory storage instead of real Google Sheets
        """
        self.demo_mode = demo_mode
        self.client = None
        self.sheet = None
        
        # In-memory storage for demo mode
        self.demo_users = []
        
        if not demo_mode and GSPREAD_AVAILABLE:
            self._init_google_sheets()
        else:
            print("Running in DEMO MODE - using in-memory storage")
            self._init_demo_data()
    
    def _init_google_sheets(self):
        """Initialize real Google Sheets connection"""
        try:
            creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            spreadsheet_id = os.environ.get('GOOGLE_SPREADSHEET_ID')
            
            if not creds_path or not spreadsheet_id:
                print("Warning: Google Sheets credentials not configured. Falling back to demo mode.")
                self.demo_mode = True
                self._init_demo_data()
                return
            
            # Define the required scopes
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate with service account
            creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
            self.client = gspread.authorize(creds)
            
            # Open the spreadsheet
            self.sheet = self.client.open_by_key(spreadsheet_id).worksheet('Users')
            
            # Ensure headers exist
            headers = self.sheet.row_values(1)
            if not headers:
                self.sheet.append_row([
                    'user_id', 'name', 'email', 'password_hash', 
                    'created_at', 'updated_at'
                ])
            
            print("Google Sheets connection initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Google Sheets: {e}")
            print("Falling back to demo mode")
            self.demo_mode = True
            self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize demo data for testing"""
        # Create a demo user
        demo_password_hash = bcrypt.hashpw(
            "password123".encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        demo_user = {
            'user_id': str(uuid.uuid4()),
            'name': 'Demo User',
            'email': 'demo@loopync.com',
            'password_hash': demo_password_hash,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        self.demo_users = [demo_user]
        print("Demo data initialized. You can login with:")
        print("  Email: demo@loopync.com")
        print("  Password: password123")
    
    def create_user(self, name: str, email: str, password: str) -> Dict:
        """
        Create a new user.
        
        Args:
            name: User's full name
            email: User's email address (must be unique)
            password: User's plaintext password (will be hashed)
            
        Returns:
            Dictionary containing the created user data (without password_hash)
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing = self.find_user_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create timestamps
        now = datetime.now(timezone.utc).isoformat()
        
        user_data = {
            'user_id': user_id,
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'created_at': now,
            'updated_at': now
        }
        
        if self.demo_mode:
            # Add to in-memory storage
            self.demo_users.append(user_data.copy())
        else:
            # Add to Google Sheets
            self.sheet.append_row([
                user_id, name, email, password_hash, now, now
            ], value_input_option='USER_ENTERED')
        
        # Return user data without password_hash
        return {
            'user_id': user_data['user_id'],
            'name': user_data['name'],
            'email': user_data['email'],
            'created_at': user_data['created_at']
        }
    
    def find_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Find a user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User dictionary if found, None otherwise
        """
        if self.demo_mode:
            for user in self.demo_users:
                if user['email'].lower() == email.lower():
                    return user.copy()
            return None
        else:
            try:
                # Search for email in column C (email column)
                cell = self.sheet.find(email, in_column=3)
                if cell:
                    # Get the entire row
                    row_values = self.sheet.row_values(cell.row)
                    if len(row_values) >= 6:
                        return {
                            'user_id': row_values[0],
                            'name': row_values[1],
                            'email': row_values[2],
                            'password_hash': row_values[3],
                            'created_at': row_values[4],
                            'updated_at': row_values[5]
                        }
                return None
            except Exception as e:
                print(f"Error finding user: {e}")
                return None
    
    def find_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Find a user by user_id.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User dictionary if found, None otherwise
        """
        if self.demo_mode:
            for user in self.demo_users:
                if user['user_id'] == user_id:
                    return user.copy()
            return None
        else:
            try:
                # Search for user_id in column A
                cell = self.sheet.find(user_id, in_column=1)
                if cell:
                    row_values = self.sheet.row_values(cell.row)
                    if len(row_values) >= 6:
                        return {
                            'user_id': row_values[0],
                            'name': row_values[1],
                            'email': row_values[2],
                            'password_hash': row_values[3],
                            'created_at': row_values[4],
                            'updated_at': row_values[5]
                        }
                return None
            except Exception as e:
                print(f"Error finding user: {e}")
                return None
    
    def verify_password(self, email: str, password: str) -> Optional[Dict]:
        """
        Verify user credentials and return user data if valid.
        
        Args:
            email: User's email
            password: User's plaintext password
            
        Returns:
            User dictionary (without password_hash) if credentials are valid, None otherwise
        """
        user = self.find_user_by_email(email)
        if not user:
            return None
        
        # Verify password
        password_hash = user['password_hash'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), password_hash):
            # Return user data without password_hash
            return {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'created_at': user['created_at']
            }
        
        return None
    
    def update_user(self, user_id: str, name: Optional[str] = None) -> Optional[Dict]:
        """
        Update user information.
        
        Args:
            user_id: User ID to update
            name: New name (optional)
            
        Returns:
            Updated user dictionary if successful, None if user not found
        """
        if self.demo_mode:
            for user in self.demo_users:
                if user['user_id'] == user_id:
                    if name:
                        user['name'] = name
                    user['updated_at'] = datetime.now(timezone.utc).isoformat()
                    return {
                        'user_id': user['user_id'],
                        'name': user['name'],
                        'email': user['email'],
                        'created_at': user['created_at']
                    }
            return None
        else:
            try:
                cell = self.sheet.find(user_id, in_column=1)
                if cell:
                    row = cell.row
                    if name:
                        self.sheet.update_cell(row, 2, name)
                    
                    # Update timestamp
                    now = datetime.now(timezone.utc).isoformat()
                    self.sheet.update_cell(row, 6, now)
                    
                    # Retrieve and return updated user
                    return self.find_user_by_id(user_id)
                return None
            except Exception as e:
                print(f"Error updating user: {e}")
                return None
    
    def update_user_password(self, email: str, new_password: str) -> bool:
        """
        Update user password.
        
        Args:
            email: User's email
            new_password: New plaintext password (will be hashed)
            
        Returns:
            True if successful, False otherwise
        """
        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if self.demo_mode:
            for user in self.demo_users:
                if user['email'].lower() == email.lower():
                    user['password_hash'] = password_hash
                    user['updated_at'] = datetime.now(timezone.utc).isoformat()
                    return True
            return False
        else:
            try:
                cell = self.sheet.find(email, in_column=3)
                if cell:
                    row = cell.row
                    # Update password hash (column D)
                    self.sheet.update_cell(row, 4, password_hash)
                    # Update timestamp (column F)
                    self.sheet.update_cell(row, 6, datetime.now(timezone.utc).isoformat())
                    return True
                return False
            except Exception as e:
                print(f"Error updating password: {e}")
                return False
    
    def get_all_users(self) -> List[Dict]:
        """
        Get all users (without password hashes).
        
        Returns:
            List of user dictionaries
        """
        if self.demo_mode:
            return [{
                'user_id': u['user_id'],
                'name': u['name'],
                'email': u['email'],
                'created_at': u['created_at']
            } for u in self.demo_users]
        else:
            try:
                records = self.sheet.get_all_records()
                return [{
                    'user_id': r['user_id'],
                    'name': r['name'],
                    'email': r['email'],
                    'created_at': r['created_at']
                } for r in records]
            except Exception as e:
                print(f"Error getting all users: {e}")
                return []


# Global instance - will be initialized in server.py
sheets_db = None


def init_sheets_db(demo_mode=True):
    """Initialize the global sheets_db instance"""
    global sheets_db
    sheets_db = SheetsDB(demo_mode=demo_mode)
    return sheets_db
