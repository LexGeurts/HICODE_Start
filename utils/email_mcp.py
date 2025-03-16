"""
Model Context Protocol (MCP) implementation for email connectivity in MailoBot
"""
import imaplib
import email
import json
import os
from email.header import decode_header
from typing import Dict, List, Any, Optional, Text

class EmailMCP:
    """
    A Model Context Protocol implementation for email connectivity
    Maintains context about email sessions and provides methods for email operations
    """
    
    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """
        Initialize the EmailMCP with optional settings
        
        Args:
            settings: Dictionary with IMAP settings (host, port, username, password, tls)
        """
        self.imap_conn = None
        self.settings = settings
        self.context = {
            "connected": False,
            "mailbox": None,
            "current_folder": "INBOX",
            "recent_emails": [],
            "unread_count": 0,
            "selected_email": None
        }
    
    def connect(self, settings: Optional[Dict[str, Any]] = None):
        """
        Connect to the email server using IMAP
        
        Args:
            settings: Dictionary with IMAP settings (can override init settings)
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if settings:
            self.settings = settings
        
        if not self.settings:
            raise ValueError("Email settings not provided")
        
        try:
            # Connect to the IMAP server
            if self.settings.get('tls', True):
                self.imap_conn = imaplib.IMAP4_SSL(self.settings['host'], int(self.settings.get('port', 993)))
            else:
                self.imap_conn = imaplib.IMAP4(self.settings['host'], int(self.settings.get('port', 143)))
            
            # Login with credentials
            self.imap_conn.login(self.settings['username'], self.settings['password'])
            
            # Update context
            self.context["connected"] = True
            return True
        
        except Exception as e:
            print(f"Error connecting to email server: {e}")
            self.context["connected"] = False
            self.context["error"] = str(e)
            return False
    
    def disconnect(self):
        """Close the IMAP connection if active"""
        if self.imap_conn:
            try:
                self.imap_conn.logout()
            except:
                pass
            self.imap_conn = None
            self.context["connected"] = False
    
    def select_folder(self, folder: str = "INBOX"):
        """
        Select a mailbox folder
        
        Args:
            folder: Mailbox folder name
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            status, data = self.imap_conn.select(folder)
            if status == "OK":
                self.context["current_folder"] = folder
                self.context["mailbox"] = data
                return True
            return False
        except Exception as e:
            print(f"Error selecting folder {folder}: {e}")
            return False
    
    def is_connected(self):
        """Check if connected to email server"""
        return self.imap_conn is not None and self.context.get("connected", False)
    
    def get_unread_count(self):
        """Get the number of unread emails in the current folder"""
        if not self.is_connected():
            return 0
            
        try:
            self.select_folder(self.context["current_folder"])
            status, data = self.imap_conn.search(None, 'UNSEEN')
            if status == "OK":
                unread_ids = data[0].split()
                count = len(unread_ids)
                self.context["unread_count"] = count
                return count
            return 0
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
    
    def get_recent_emails(self, limit: int = 5):
        """
        Get the most recent emails
        
        Args:
            limit: Maximum number of emails to retrieve
            
        Returns:
            List of email dictionaries
        """
        if not self.is_connected():
            return []
            
        try:
            self.select_folder(self.context["current_folder"])
            status, data = self.imap_conn.search(None, 'ALL')
            if status != "OK":
                return []
                
            email_ids = data[0].split()
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            recent_ids.reverse()  # Most recent first
            
            emails = []
            for email_id in recent_ids:
                email_data = self.fetch_email(email_id)
                if email_data:
                    emails.append(email_data)
            
            # Update context
            self.context["recent_emails"] = emails
            return emails
        except Exception as e:
            print(f"Error getting recent emails: {e}")
            return []
    
    def fetch_email(self, email_id):
        """
        Fetch a specific email by ID
        
        Args:
            email_id: The email ID to fetch
            
        Returns:
            Dict containing email data or None if error
        """
        if not self.is_connected():
            return None
            
        try:
            status, data = self.imap_conn.fetch(email_id, '(RFC822)')
            if status != "OK":
                return None
                
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract subject
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
                
            # Extract sender
            sender = decode_header(msg["From"])[0][0]
            if isinstance(sender, bytes):
                sender = sender.decode()
                
            # Extract date
            date = msg["Date"]
            
            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode()
                            break
                        except:
                            pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode()
                except:
                    body = "Unable to decode message body"
            
            # Extract attachments
            attachments = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                        
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type()
                        })
            
            # Check read status
            status, read_data = self.imap_conn.fetch(email_id, '(FLAGS)')
            read = b'\\Seen' in read_data[0]
            
            email_data = {
                "id": email_id.decode() if isinstance(email_id, bytes) else email_id,
                "subject": subject,
                "from": sender,
                "date": date,
                "body": body,
                "read": read,
                "has_attachments": len(attachments) > 0,
                "attachments": attachments
            }
            
            return email_data
        except Exception as e:
            print(f"Error fetching email {email_id}: {e}")
            return None
    
    def mark_as_read(self, email_id):
        """Mark an email as read"""
        if not self.is_connected():
            return False
            
        try:
            self.imap_conn.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False
    
    def search_emails(self, criteria: Dict[str, Any]):
        """
        Search for emails using various criteria
        
        Args:
            criteria: Dictionary with search parameters (sender, subject, date, etc.)
            
        Returns:
            List of email dictionaries matching criteria
        """
        if not self.is_connected():
            return []
            
        try:
            search_query = []
            
            if 'sender' in criteria:
                search_query.append(f'FROM "{criteria["sender"]}"')
            
            if 'subject' in criteria:
                search_query.append(f'SUBJECT "{criteria["subject"]}"')
                
            if 'since' in criteria:
                search_query.append(f'SINCE "{criteria["since"]}"')
                
            if 'unread' in criteria and criteria['unread']:
                search_query.append('UNSEEN')
                
            if 'has_attachments' in criteria and criteria['has_attachments']:
                search_query.append('BODY "Content-Disposition: attachment"')
            
            # Convert the query to IMAP format
            query = ' '.join(search_query)
            
            # Execute search
            self.select_folder(self.context["current_folder"])
            status, data = self.imap_conn.search(None, query)
            if status != "OK":
                return []
                
            email_ids = data[0].split()
            
            # Limit results
            limit = criteria.get('limit', 10)
            if len(email_ids) > limit:
                email_ids = email_ids[:limit]
            
            # Fetch emails
            results = []
            for email_id in email_ids:
                email_data = self.fetch_email(email_id)
                if email_data:
                    results.append(email_data)
                    
            return results
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    def get_context(self):
        """Get the current MCP context"""
        return self.context
    
    def update_context(self, updates: Dict[str, Any]):
        """
        Update the MCP context
        
        Args:
            updates: Dictionary with context updates
        """
        self.context.update(updates)
