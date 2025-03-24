from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

# Import all actions from modules
from .email_actions import (
    ActionCheckEmail,
    ActionTestEmailConnection
)

# Add a new action for reading emails
class ActionReadEmail(Action):
    def name(self) -> Text:
        return "action_read_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get email ID from context or metadata
        email_id = tracker.get_slot("email_id")
        metadata = tracker.get_latest_message().get("metadata", {})
        
        if not email_id and metadata.get("emailId"):
            email_id = metadata.get("emailId")
            
        if not email_id:
            dispatcher.utter_message(text="I couldn't find which email you want to read. Please specify an email.")
            return []
            
        # Here we would normally fetch the email content
        # For now, we'll just return a custom response to notify the frontend
        dispatcher.utter_message(
            json_message={
                "action": {
                    "name": "read_email",
                    "emailId": email_id
                },
                "context": {
                    "current_email_id": email_id
                }
            }
        )
        
        return [SlotSet("current_email_id", email_id)]

# Add action for collecting sender when forwarding emails
class ActionCollectSender(Action):
    def name(self) -> Text:
        return "action_collect_sender"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get email ID from context
        email_id = tracker.get_slot("email_id")
        current_email = tracker.get_slot("current_email")
        
        # Ask user for recipient address
        dispatcher.utter_message(text="Who would you like to forward this email to?")
        
        # Return action with JSON message to notify frontend
        dispatcher.utter_message(
            json_message={
                "action": {
                    "name": "forward_email",
                    "emailId": email_id,
                    "email": current_email
                },
                "context": {
                    "forwarding": True,
                    "email_id": email_id
                }
            }
        )
        
        return [SlotSet("forwarding_email", True)]

# Export all actions (central import for custom actions; adjust as needed)
__all__ = [
    'ActionCheckEmail',
    'ActionTestEmailConnection',
    'ActionReadEmail',
    'ActionCollectSender'
]
