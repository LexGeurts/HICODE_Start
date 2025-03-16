"""
Actions related to email drafting
"""
import json
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionCollectEdits(Action):
    """Action to collect edits for email draft"""

    def name(self) -> Text:
        return "action_collect_edits"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="What changes would you like to make to the draft?")
        return []


class ActionConfirmSend(Action):
    """Action to confirm sending an email"""

    def name(self) -> Text:
        return "action_confirm_send"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        recipient = tracker.get_slot("email_recipient") or "the recipient"
        dispatcher.utter_message(text=f"Are you ready to send this email to {recipient}?")
        return []


class ActionSaveDraft(Action):
    """Action to save email draft"""

    def name(self) -> Text:
        return "action_save_draft"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Your draft has been saved. You can access it later to continue editing or send it.")
        return []


class ActionConfirmDiscard(Action):
    """Action to confirm discarding an email draft"""

    def name(self) -> Text:
        return "action_confirm_discard"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Are you sure you want to discard this draft? This action cannot be undone.")
        return []


class ActionDraftEmail(Action):
    """Action to draft an email based on provided information"""

    def name(self) -> Text:
        return "action_draft_email"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        try:
            # Get email recipient from slot or context - be more defensive with fallbacks
            recipient = None
            
            # Try to get recipient from slots
            if tracker.get_slot("email_recipient"):
                recipient = tracker.get_slot("email_recipient")
            
            # If not in slots, try to get from entities
            if not recipient:
                for entity in tracker.latest_message.get("entities", []):
                    if entity["entity"] == "sender":
                        recipient = entity["value"]
                        break
            
            # If still not found, use a default
            recipient = recipient or "the recipient"
            
            # Get subject with similar defensive approach
            subject = tracker.get_slot("email_subject") or "your message"
            
            # Determine if this is a reply
            is_reply = False
            intent = tracker.latest_message.get("intent", {}).get("name", "")
            if intent == "reply_to_email":
                is_reply = True
                action_type = "reply"
            else:
                action_type = "draft"
            
            # Customize message based on whether this is a reply or new email
            if is_reply:
                dispatcher.utter_message(text=f"I'm drafting a reply to {recipient}...")
            else:
                dispatcher.utter_message(text=f"Drafting an email to {recipient} with subject '{subject}'...")
            
            # Set slots for further steps in the conversation
            slots_to_set = [SlotSet("email_recipient", recipient), SlotSet("email_subject", subject)]
            
            # If this is a reply, we don't ask for subject
            if is_reply:
                # For a reply, we might want to set a different flow
                slots_to_set.append(SlotSet("active_flow", "email_replying"))
            else:
                slots_to_set.append(SlotSet("active_flow", "email_drafting"))
            
            # Provide additional instructions
            dispatcher.utter_message(text="(This is a simulation - in a real implementation, this would create an actual email draft)")
            
            return slots_to_set
            
        except Exception as e:
            # Log the error and return a graceful message
            print(f"Error in action_draft_email: {str(e)}")
            dispatcher.utter_message(text="I encountered an issue while trying to draft your email. Let's try again.")
            return []


class ActionSendEmail(Action):
    """Action to send a drafted email"""

    def name(self) -> Text:
        return "action_send_email"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        try:
            recipient = tracker.get_slot("email_recipient") or "the recipient"
            
            dispatcher.utter_message(text=f"Your email has been sent to {recipient}.")
            dispatcher.utter_message(text="(This is a simulation - in a real implementation, this would send an actual email)")
            
            # Reset email-related slots after sending
            return [
                SlotSet("email_recipient", None),
                SlotSet("email_subject", None),
                SlotSet("email_content", None),
                SlotSet("active_flow", "main_flow")
            ]
        
        except Exception as e:
            # Log the error and provide a graceful message
            print(f"Error in action_send_email: {str(e)}")
            dispatcher.utter_message(text="I encountered an issue while trying to send your email. Let's try again.")
            return []


class ActionDraftComplete(Action):
    def name(self) -> Text:
        return "action_draft_complete"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        recipient = tracker.get_slot("email_recipient") or "the recipient"
        subject = tracker.get_slot("email_subject") or "the subject"
        content = tracker.get_slot("email_content") or "the email content"
        
        email_preview = f"To: {recipient}\nSubject: {subject}\n\n{content}"
        
        dispatcher.utter_message(text=f"I've drafted your email:\n\n{email_preview}")
        return []


class ActionCollectDraftInfo(Action):
    def name(self) -> Text:
        return "action_collect_draft_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Check if we already have recipient information
            recipient = tracker.get_slot("email_recipient")
            
            if not recipient:
                dispatcher.utter_message(text="Who would you like to send this email to?")
                return []
            
            # Check if we have subject information
            subject = tracker.get_slot("email_subject")
            
            if not subject:
                dispatcher.utter_message(text="What should be the subject of your email?")
                return []
            
            # If we have all needed info, prompt for content
            dispatcher.utter_message(text=f"Great! Now, what would you like to say in your email to {recipient}?")
            return []
        
        except Exception as e:
            # Log the error and return a graceful message
            print(f"Error in action_collect_draft_info: {str(e)}")
            dispatcher.utter_message(text="I encountered an issue while collecting your email information. Let's try again.")
            return []


class ActionReplyToEmail(Action):
    """Action to reply to an email"""

    def name(self) -> Text:
        return "action_reply_to_email"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        try:
            # Get context or use current conversation
            context = tracker.get_slot("context") or {}
            
            # Try to get the sender from the current email context
            recipient = None
            if "email" in context and "from" in context["email"]:
                recipient = context["email"]["from"]
            
            # If we couldn't get it from context, check entities
            if not recipient:
                for entity in tracker.latest_message.get("entities", []):
                    if entity["entity"] == "sender":
                        recipient = entity["value"]
                        break
            
            # Default if no recipient found
            recipient = recipient or "the sender"
            
            # Get the subject with "Re:" prefix
            subject = None
            if "email" in context and "subject" in context["email"]:
                if not context["email"]["subject"].startswith("Re:"):
                    subject = f"Re: {context['email']['subject']}"
                else:
                    subject = context["email"]["subject"]
            
            # Default subject
            subject = subject or "your email"
            
            dispatcher.utter_message(text=f"I'll help you draft a reply to {recipient}.")
            
            # Set slots for the email drafting flow
            return [
                SlotSet("email_recipient", recipient),
                SlotSet("email_subject", subject),
                SlotSet("active_flow", "email_drafting"),
                SlotSet("is_reply", True)
            ]
        
        except Exception as e:
            print(f"Error in action_reply_to_email: {str(e)}")
            dispatcher.utter_message(text="I encountered an issue preparing your reply. Let's try again.")
            return []
