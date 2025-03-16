"""
Actions related to email search
"""
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionCollectSender(Action):
    """Action to collect sender information for email search"""

    def name(self) -> Text:
        return "action_collect_sender"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Which sender's emails are you looking for?")
        return []


class ActionCollectSubject(Action):
    """Action to collect subject information for email search"""

    def name(self) -> Text:
        return "action_collect_subject"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="What subject or keywords are you looking for in the email subject line?")
        return []


class ActionCollectDate(Action):
    """Action to collect date information for email search"""

    def name(self) -> Text:
        return "action_collect_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="What date or date range are you looking for? (e.g., today, last week, between June 1-15, etc.)")
        return []


class ActionCollectContent(Action):
    """Action to collect content information for email search"""

    def name(self) -> Text:
        return "action_collect_content"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="What words or phrases are you looking for in the email body?")
        return []


class ActionCollectAttachment(Action):
    """Action to collect attachment information for email search"""

    def name(self) -> Text:
        return "action_collect_attachment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="What type of attachment are you looking for? (e.g., PDF, images, spreadsheets)")
        return []


class ActionSearchEmails(Action):
    """Action to handle email search requests"""

    def name(self) -> Text:
        return "action_search_emails"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # This would connect to an email service in a real implementation
        dispatcher.utter_message(text="Searching for emails matching your criteria...")
        dispatcher.utter_message(text="(This is a simulation - in a real implementation, this would search your actual emails)")
        
        # Return a sample response
        dispatcher.utter_message(text="I found 5 emails matching your search criteria. Would you like to refine your search or view any of these emails?")
        
        return []
