"""
Test script for EmailMCP to verify direct IMAP connection and email fetching
"""
import json
import sys
from email_mcp import EmailMCP


def test_email_connection(settings):
    """Test email connection and fetch recent emails"""
    print(
        f"Testing connection to {settings['host']}:{settings['port']} as {settings['username']}")

    # Create EmailMCP instance
    mcp = EmailMCP(settings)

    # Connect to IMAP server
    print("Connecting to IMAP server...")
    connected = mcp.connect()
    print(f"Connection status: {'Connected' if connected else 'Failed'}")

    if not connected:
        print(f"Connection error: {mcp.context.get('error', 'Unknown error')}")
        return False

    # Get unread count
    print("Getting unread count...")
    unread = mcp.get_unread_count()
    print(f"Unread count: {unread}")

    # Get recent emails
    print("Fetching recent emails...")
    emails = mcp.get_recent_emails(limit=5)
    print(f"Found {len(emails)} recent emails")

    # Print email details
    for i, email in enumerate(emails):
        print(f"\nEmail {i+1}:")
        print(f"  From: {email['from']}")
        print(f"  Subject: {email['subject']}")
        print(f"  Date: {email['date']}")
        print(f"  Read: {'Yes' if email['read'] else 'No'}")
        print(
            f"  Has attachments: {'Yes' if email['has_attachments'] else 'No'}")

    # Disconnect
    mcp.disconnect()
    print("\nTest completed and connection closed")
    return True


if __name__ == "__main__":
    # Check if settings file provided as argument
    if len(sys.argv) > 1:
        settings_file = sys.argv[1]
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        # Example settings, replace with your own for testing
        settings = {
            "host": "imap.gmail.com",
            "port": 993,
            "username": "your.email@gmail.com",
            "password": "your-app-password",
            "tls": True
        }

        print("No settings file provided. You can create a settings.json file with your IMAP settings")
        print("Using default settings (you need to edit these)")

        # Ask for confirmation before proceeding with default settings
        confirmation = input("Continue with default settings? (yes/no): ")
        if confirmation.lower() != "yes":
            print("Test aborted")
            sys.exit(1)

    # Run the test
    test_email_connection(settings)
