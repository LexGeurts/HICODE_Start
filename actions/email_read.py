"""
Actions related to reading emails
"""
import json
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionCheckEmails(Action):
    def name(self) -> Text:
        return "action_check_emails"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, we'd connect to an email service
        # For now, we'll simulate with a custom action response
        
        # Send a custom action request to the frontend
        dispatcher.utter_message(json.dumps({
            "custom": {
                "action": {
                    "name": "check_emails"
                }
            }
        }))
        
        return [SlotSet("new_emails_count", 1)]  # Simulate finding 1 new email


class ActionReadEmail(Action):
    def name(self) -> Text:
        return "action_read_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract the email ID from the context
        context = tracker.get_slot("context") or {}
        email_id = None
        
        if context.get("type") == "new_email_notification" and context.get("emailId"):
            email_id = context.get("emailId")
        
        # Send a custom action to read the specific email
        dispatcher.utter_message(json.dumps({
            "custom": {
                "action": {
                    "name": "read_email",
                    "emailId": email_id
                }
            }
        }))
        
        return [SlotSet("selected_email", True)]


class ActionShowInbox(Action):
    def name(self) -> Text:
        return "action_show_inbox"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Send a custom action request to show the inbox
        dispatcher.utter_message(json.dumps({
            "custom": {
                "action": {
                    "name": "show_inbox"
                }
            }
        }))
        
        return []


class ActionShowSettings(Action):
    def name(self) -> Text:
        return "action_show_settings"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Send a custom action request to show the settings dialog
        dispatcher.utter_message(json.dumps({
            "custom": {
                "action": {
                    "name": "settings_dialog"
                }
            }
        }))
        
        return []


class ActionReadRecentEmail(Action):
    def name(self) -> Text:
        return "action_read_recent_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # This would fetch the most recent email from context
        context = tracker.get_slot("context") or {}
        
        if context.get("recentEmails") and len(context.get("recentEmails")) > 0:
            recent_email = context.get("recentEmails")[0]
            email_id = recent_email.get("id")
            
            # Send a custom action to read the specific email
            dispatcher.utter_message(json.dumps({
                "custom": {
                    "action": {
                        "name": "read_email",
                        "emailId": email_id
                    }
                }
            }))
            
            return [SlotSet("selected_email", True)]
        else:
            dispatcher.utter_message("I don't see any recent emails to show you.")
            return []


class ActionNotifyNewEmails(Action):
    def name(self) -> Text:
        return "action_notify_new_emails"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the number of new emails from the slot
        new_emails_count = tracker.get_slot("new_emails_count") or 0
        
        if new_emails_count > 0:
            dispatcher.utter_message(
                text=f"You have {new_emails_count} new email(s). Would you like me to read them?")
        else:
            dispatcher.utter_message(text="You don't have any new emails at the moment.")
        
        return []


class ActionFetchEmails(Action):
    def name(self) -> Text:
        return "action_fetch_emails"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # This would connect to an email service in a real implementation
        # For demo purposes, let's simulate fetching emails
        
        # Simulate having emails
        has_emails = True
        emails = [
            {"id": 1, "subject": "Meeting tomorrow", "sender": "team@example.com"},
            {"id": 2, "subject": "Project update", "sender": "manager@example.com"},
            {"id": 3, "subject": "Weekly newsletter", "sender": "news@example.com"}
        ]
        
        return [SlotSet("has_emails", has_emails), SlotSet("emails", emails)]


class ActionDisplayEmailList(Action):
    def name(self) -> Text:
        return "action_display_email_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        emails = tracker.get_slot("emails") or []
                
        if emails:
            email_list = "\n".join([f"- {e['id']}: {e['subject']} from {e['sender']}" for e in emails])
            dispatcher.utter_message(text=f"Here are your emails:\n{email_list}")
        else:
            dispatcher.utter_message(text="No emails to display.")
        
        return []


class ActionPostReadOptions(Action):
    def name(self) -> Text:
        return "action_post_read_options"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Would you like to reply to this email, forward it, archive it, or delete it?")
        return []
