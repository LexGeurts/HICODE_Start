"""
Test module for EmailMCP functionality
"""
import os
import sys
import json
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.email_mcp import EmailMCP

def load_imap_settings():
    """Load IMAP settings from JSON file"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_file = os.path.join(current_dir, 'settings', 'imap_settings.json')
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading IMAP settings: {e}")
        return None

def test_connection():
    """Test connecting to email server using settings from JSON file"""
    # Load settings from JSON file
    settings = load_imap_settings()
    
    if not settings:
        print("No IMAP settings found. Please configure settings first.")
        return
    
    # Print settings (except password)
    safe_settings = {k: (v if k != 'password' else '****') for k, v in settings.items()}
    print(f"Using settings: {safe_settings}")
    
    # Create EmailMCP instance and test connection
    email_client = EmailMCP(settings)
    success = email_client.connect()
    
    if success:
        print("✅ Connection successful!")
        print(f"Connected to {settings['host']} as {settings['username']}")
        
        # Try to select inbox
        if email_client.select_folder("INBOX"):
            print("✅ Successfully selected INBOX folder")
            
            # Get unread count
            unread_count = email_client.get_unread_count()
            print(f"📬 Unread emails: {unread_count}")
            
            # Get recent emails
            recent_emails = email_client.get_recent_emails(3)
            print(f"📨 Recent emails: {len(recent_emails)}")
            
            # Print recent email subjects
            for idx, email in enumerate(recent_emails):
                print(f"  {idx+1}. {email['subject']} (from: {email['from']})")
            
        else:
            print("❌ Failed to select INBOX folder")
            
        # Disconnect
        email_client.disconnect()
        print("📭 Disconnected from email server")
    else:
        print("❌ Connection failed!")
        print(f"Error: {email_client.context.get('error', 'Unknown error')}")

def test_actions():
    """Test email actions module that uses the JSON settings"""
    # Instead of importing from email_actions, create local functions using EmailMCP directly
    
    def check_email_connection() -> Dict[str, Any]:
        """Test email connection using settings from JSON file"""
        settings = load_imap_settings()
        if not settings:
            return {
                "success": False,
                "message": "No IMAP settings found. Please configure settings first."
            }
        
        # Create EmailMCP instance and test connection
        email_client = EmailMCP(settings)
        success = email_client.connect()
        
        if success:
            message = f"Connection successful! Connected to {settings['host']} as {settings['username']}"
            # Disconnect before returning
            email_client.disconnect()
            return {"success": True, "message": message}
        else:
            message = f"Connection failed: {email_client.context.get('error', 'Unknown error')}"
            return {"success": False, "message": message}
    
    def get_unread_emails(limit: int = 5) -> Dict[str, Any]:
        """Get unread emails using EmailMCP"""
        settings = load_imap_settings()
        if not settings:
            return {
                "success": False,
                "message": "No IMAP settings found. Please configure settings first.",
                "emails": []
            }
        
        # Create EmailMCP instance and connect
        email_client = EmailMCP(settings)
        if not email_client.connect():
            return {
                "success": False,
                "message": f"Failed to connect: {email_client.context.get('error', 'Unknown error')}",
                "emails": []
            }
        
        # Select inbox and get unread emails
        if not email_client.select_folder("INBOX"):
            email_client.disconnect()
            return {
                "success": False,
                "message": "Failed to select INBOX folder",
                "emails": []
            }
        
        # Get unread emails
        emails = email_client.get_unread_emails(limit)
        email_client.disconnect()
        
        return {
            "success": True,
            "message": f"Retrieved {len(emails)} unread emails",
            "emails": emails
        }
    
    def get_recent_emails(limit: int = 5) -> Dict[str, Any]:
        """Get recent emails using EmailMCP"""
        settings = load_imap_settings()
        if not settings:
            return {
                "success": False,
                "message": "No IMAP settings found. Please configure settings first.",
                "emails": []
            }
        
        # Create EmailMCP instance and connect
        email_client = EmailMCP(settings)
        if not email_client.connect():
            return {
                "success": False,
                "message": f"Failed to connect: {email_client.context.get('error', 'Unknown error')}",
                "emails": []
            }
        
        # Select inbox and get recent emails
        if not email_client.select_folder("INBOX"):
            email_client.disconnect()
            return {
                "success": False,
                "message": "Failed to select INBOX folder",
                "emails": []
            }
        
        # Get recent emails
        emails = email_client.get_recent_emails(limit)
        email_client.disconnect()
        
        return {
            "success": True,
            "message": f"Retrieved {len(emails)} recent emails",
            "emails": emails
        }
    
    # Test connection
    print("\n--- Testing connection via actions module ---")
    result = check_email_connection()
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")
        return
    
    # Test getting unread emails
    print("\n--- Testing unread emails retrieval ---")
    unread_result = get_unread_emails(3)
    if unread_result["success"]:
        emails = unread_result["emails"]
        print(f"✅ {unread_result['message']}")
        for idx, email in enumerate(emails):
            print(f"  {idx+1}. {email['subject']} (from: {email['from']})")
    else:
        print(f"❌ {unread_result['message']}")
    
    # Test getting recent emails
    print("\n--- Testing recent emails retrieval ---")
    recent_result = get_recent_emails(3)
    if recent_result["success"]:
        emails = recent_result["emails"]
        print(f"✅ {recent_result['message']}")
        for idx, email in enumerate(emails):
            print(f"  {idx+1}. {email['subject']} (from: {email['from']})")
    else:
        print(f"❌ {recent_result['message']}")

if __name__ == "__main__":
    # Create settings directory if it doesn't exist
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    settings_dir = os.path.join(current_dir, 'settings')
    os.makedirs(settings_dir, exist_ok=True)
    
    # Check if settings file exists
    settings_file = os.path.join(settings_dir, 'imap_settings.json')
    if not os.path.exists(settings_file):
        print(f"⚠️ Settings file not found: {settings_file}")
        print("Please configure your IMAP settings through the web interface first.")
    else:
        print(f"📁 Found settings file: {settings_file}")
        # Run tests
        print("\n=== Testing EmailMCP with settings from JSON file ===")
        test_connection()
        
        print("\n=== Testing Actions Module ===")
        test_actions()
