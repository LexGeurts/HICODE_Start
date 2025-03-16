"""
Actions for connecting to email using Model Context Protocol
"""
import json
import os
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Import the EmailMCP
from ..utils.email_mcp import EmailMCP

# Singleton instance of EmailMCP
email_mcp = EmailMCP()

class ActionConnectEmail(Action):
    """Action to connect to email using MCP"""

    def name(self) -> Text:
        return "action_connect_email"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        try:
            # Get IMAP settings from slot or context
            imap_settings = tracker.get_slot("imap_settings")
            
            if not imap_settings:
                dispatcher.utter_message(text="I don't have your email settings yet. Please set up your email account first.")
                return [SlotSet("email_connected", False)]
            
            # Attempt to connect using EmailMCP
            success = email_mcp.connect(imap_settings)
            
            if success:
                # Get unread count
                unread_count = email_mcp.get_unread_count()
                
                # Update context
                mcp_context = email_mcp.get_context()
                
                dispatcher.utter_message(text=f"Successfully connected to your email account. You have {unread_count} unread emails.")
                
                return [
                    SlotSet("email_connected", True),
                    SlotSet("unread_count", unread_count),
                    SlotSet("mcp_context", mcp_context)
                ]
            else:
                dispatcher.utter_message(text="Failed to connect to your email account. Please check your settings and try again.")
                return [SlotSet("email_connected", False)]
                
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while connecting to your email: {str(e)}")
            return [SlotSet("email_connected", False)]


class ActionGetRecentEmails(Action):
    """Action to get recent emails using MCP"""

    def name(self) -> Text:
        return "action_get_recent_emails"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        try:
            # Check if connected
            if not email_mcp.is_connected():
                # Try to reconnect
                imap_settings = tracker.get_slot("imap_settings")
                if imap_settings and email_mcp.connect(imap_settings):
                    dispatcher.utter_message(text="Reconnected to your email account.")
                else:
                    dispatcher.utter_message(text="Not connected to email. Please set up your email account first.")
                    return [SlotSet("email_connected", False)]
            
            # Get recent emails
            limit = tracker.get_slot("email_limit") or 5
            emails = email_mcp.get_recent_emails(int(limit))
            
            # Update MCP context
            mcp_context = email_mcp.get_context()
            
            if emails:
                # Format emails for display
                email_list = "\n".join([f"- {e['id']}: {e['subject']} from {e['from']}" for e in emails])
                dispatcher.utter_message(text=f"Here are your {len(emails)} most recent emails:\n{email_list}")
            else:
                dispatcher.utter_message(text="No recent emails found.")
            
            return [
                SlotSet("recent_emails", emails),
                SlotSet("mcp_context", mcp_context)
            ]
                
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while fetching recent emails: {str(e)}")
            return []


class ActionSearchEmailsMCP(Action):
    """Action to search emails using MCP"""

    def name(self) -> Text:
        return "action_search_emails_mcp"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        try:
            # Check if connected
            if not email_mcp.is_connected():
                dispatcher.utter_message(text="Not connected to email. Please set up your email account first.")
                return [SlotSet("email_connected", False)]
            
            # Build search criteria from slots
            criteria = {}
            
            if tracker.get_slot("search_sender"):
                criteria["sender"] = tracker.get_slot("search_sender")
                
            if tracker.get_slot("search_subject"):
                criteria["subject"] = tracker.get_slot("search_subject")
                
            if tracker.get_slot("search_date"):
                criteria["since"] = tracker.get_slot("search_date")
                
            if tracker.get_slot("search_attachment") == "True":
                criteria["has_attachments"] = True
            
            # Search emails
            results = email_mcp.search_emails(criteria)
            
            # Update MCP context
            mcp_context = email_mcp.get_context()
            
            if results:
                dispatcher.utter_message(text=f"Found {len(results)} emails matching your criteria.")
                # Format emails for display
                email_list = "\n".join([f"- {e['id']}: {e['subject']} from {e['from']}" for e in results])
                dispatcher.utter_message(text=email_list)
            else:
                dispatcher.utter_message(text="No emails found matching your criteria.")
            
            return [
                SlotSet("search_results", results),
                SlotSet("mcp_context", mcp_context)
            ]
                
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while searching emails: {str(e)}")
            return []
