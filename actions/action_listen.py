from typing import Dict, Text, List, Any
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class ActionListenForSender(Action):
    """Custom action to listen for and collect sender information in email context."""
    
    def name(self) -> Text:
        return "action_listen"
    
    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Execute this action to collect sender information from user input."""
        
        # Get the latest user message
        latest_message = tracker.latest_message.get('text', '')
        
        # Check if the current intent is related to reading emails
        intent = tracker.latest_message.get('intent', {}).get('name', '')
        email_related_intents = ['read_email', 'search_emails', 'check_email']
        
        # Current sender value from slots
        current_sender = tracker.get_slot('sender')
        
        # If we already have a sender value, don't overwrite it
        if current_sender:
            return []
            
        # Extract potential sender information from the message
        
        sender = None
        
        # Check if the message contains email-like patterns
        if '@' in latest_message:
            # Simple extraction of potential email address
            words = latest_message.split()
            for word in words:
                if '@' in word:
                    sender = word.strip('.,;:!?')
                    break
        
        # If no email-like pattern, check for names
        # This assumes names are mentioned after "from" or similar phrases
        elif 'from' in latest_message.lower():
            parts = latest_message.lower().split('from')
            if len(parts) > 1:
                potential_sender = parts[1].strip().split(' ')[0]
                if potential_sender and len(potential_sender) > 1:
                    sender = potential_sender
        
        # If we found a sender, set the slot
        if sender:
            # Log for debugging
            print(f"Setting sender slot to: {sender}")
            return [SlotSet("sender", sender)]
        else:
            dispatcher.utter_message("I'm not sure which sender you're looking for. Could you please specify?")


# Otherwise collect slots will be implemented below