import json
import os

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Import EmailMCP
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
class ActionCheckEmail(Action):
    def name(self) -> Text:
        return "action_check_emails"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # imap_settings = tracker.get_slot("imap_settings")
        """Get an initialized email client with settings from the JSON file"""
        imap_settings = load_imap_settings()
        options = tracker.get_latest_message().get("metadata", {}).get("options", {})
        email_limit = tracker.get_latest_message().get(
            "metadata", {}).get("email_limit", 5)

        # Default response
        response = "I couldn't check your emails. Please make sure your email settings are correct."

        # Set default context
        context = {
            "connected": False,
            "emails": [],
            "recent_emails": [],
            "unread_count": 0
        }

        if not imap_settings:
            dispatcher.utter_message(text=response)
            return [SlotSet("mcp_context", context),
                    SlotSet("email_connected", False)]

        try:
            # Initialize MCP
            mcp = EmailMCP(imap_settings)

            # Connect to IMAP server
            connected = mcp.connect()

            if connected:
                # Get emails
                folder = options.get("folder", "INBOX")
                limit = int(options.get("limit", email_limit))

                # Select folder
                mcp.select_folder(folder)

                # Get unread count
                unread_count = mcp.get_unread_count()

                # Get recent emails
                emails = mcp.get_recent_emails(limit=limit)

                # Update context
                context = mcp.get_context()
                context["connected"] = True
                context["emails"] = emails
                context["recent_emails"] = emails
                context["unread_count"] = unread_count

                # Format response
                if emails:
                    if unread_count > 0:
                        response = f"You have {unread_count} unread email(s). I found {len(emails)} recent emails in your {folder} folder."
                    else:
                        response = f"I found {len(emails)} recent emails in your {folder} folder, but no unread emails."
                else:
                    response = f"I checked your {folder} folder, but didn't find any recent emails."
            else:
                # Connection failed
                context = mcp.get_context()  # Get error information
                response = f"I couldn't connect to your email server. Error: {context.get('error', 'Unknown error')}"

            # Close connection
            mcp.disconnect()

        except Exception as e:
            print(f"Error in email action: {e}")
            context["error"] = str(e)
            response = f"Sorry, I encountered an error checking your emails: {str(e)}"

        # Send response with both text and custom message format
        dispatcher.utter_message(text=response)
        
        # Add a custom message with the action and context information
        # This is what the frontend looks for in handleRasaAction
        action_data = {
            "name": "check_email",
        }
        
        # Only add these fields if they were successfully retrieved
        if context.get("connected", False):
            action_data["unread_count"] = context.get("unread_count", 0)
            action_data["emails"] = context.get("emails", [])
            
        dispatcher.utter_message(
            json_message={
                "action": action_data,
                "context": context
            }
        )

        # Update slots
        return [
            SlotSet("mcp_context", context),
            SlotSet("email_connected", context.get("connected", False)),
            SlotSet("emails", context.get("emails", [])),
            SlotSet("has_emails", len(context.get("emails", [])) > 0)
        ]


class ActionTestEmailConnection(Action):
    def name(self) -> Text:
        return "action_test_email_connection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get IMAP settings from context
        imap_settings = tracker.get_latest_message().get(
            "metadata", {}).get("imap_settings")

        if not imap_settings:
            dispatcher.utter_message(
                text="Missing email settings. Please provide your IMAP server details.")
            return [SlotSet("email_connected", False)]

        try:
            # Initialize MCP
            mcp = EmailMCP(imap_settings)

            # Test connection
            connected = mcp.connect()

            # Get context for error reporting
            context = mcp.get_context()

            if connected:
                response = "Successfully connected to your email server!"

                # Try to get folder list if possible
                try:
                    folders = ["INBOX"]  # Default minimal folder list
                    context["folders"] = folders
                except:
                    pass

                # Try to get unread count
                try:
                    unread = mcp.get_unread_count()
                    if unread > 0:
                        response += f" You have {unread} unread emails."
                    context["unread_count"] = unread
                except:
                    pass
            else:
                response = f"Failed to connect to your email server. Error: {context.get('error', 'Unknown error')}"

            # Close connection
            mcp.disconnect()

        except Exception as e:
            context = {"connected": False, "error": str(e)}
            response = f"Error testing email connection: {str(e)}"

        # Send response with both text and custom message format
        dispatcher.utter_message(text=response)
        
        # Add a custom message for the frontend
        dispatcher.utter_message(
            json_message={
                "action": {
                    "name": "test_connection",
                    "success": connected,
                    "error": context.get("error", None)
                },
                "context": context
            }
        )

        # Update slots
        return [
            SlotSet("mcp_context", context),
            SlotSet("email_connected", context.get("connected", False))
        ]

# Additional email-related actions can be added here
