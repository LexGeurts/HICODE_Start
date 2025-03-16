"""
Actions related to conversation flow control
"""
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionActivateFlow(Action):
    """Action to activate a specific conversation flow"""

    def name(self) -> Text:
        return "action_activate_flow"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Determine which flow to activate based on the last intent
        last_intent = tracker.latest_message.get("intent", {}).get("name", "")
        
        if last_intent == "manage_inbox":
            flow_name = "email_management"
            dispatcher.utter_message(text="Let's organize your inbox. What would you like to do with your emails?")
        
        elif last_intent == "draft_email":
            flow_name = "email_drafting"
            dispatcher.utter_message(text="I'll help you draft an email. Let's start with some basic information.")
        
        elif last_intent == "search_emails":
            flow_name = "email_search"
            dispatcher.utter_message(text="I can help you find specific emails. What would you like to search for?")
        
        else:
            flow_name = "main_flow"
            dispatcher.utter_message(text="How can I help you with your emails today?")
        
        # Set the active flow slot
        return [SlotSet("active_flow", flow_name)]
