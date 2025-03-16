import json
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, ActiveLoop


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
            dispatcher.utter_message(
                text="Let's organize your inbox. What would you like to do with your emails?")

        elif last_intent == "draft_email":
            flow_name = "email_drafting"
            dispatcher.utter_message(
                text="I'll help you draft an email. Let's start with some basic information.")

        elif last_intent == "search_emails":
            flow_name = "email_search"
            dispatcher.utter_message(
                text="I can help you find specific emails. What would you like to search for?")

        else:
            flow_name = "main_flow"
            dispatcher.utter_message(
                text="How can I help you with your emails today?")

        # Set the active flow slot
        return [SlotSet("active_flow", flow_name)]


class ActionCollectFolderInfo(Action):
    """Action to collect folder information for email organization"""

    def name(self) -> Text:
        return "action_collect_folder_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="What categories would you like to organize your emails into?")
        return []


class ActionCollectFilterCriteria(Action):
    """Action to collect filter criteria for emails"""

    def name(self) -> Text:
        return "action_collect_filter_criteria"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="What criteria would you like to filter your emails by? (e.g., sender, date, subject)")
        return []


class ActionMarkEmailsRead(Action):
    """Action to mark emails as read"""

    def name(self) -> Text:
        return "action_mark_emails_read"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="Which emails would you like to mark as read? (all unread, from a specific sender, etc.)")
        return []


class ActionConfirmDelete(Action):
    """Action to confirm email deletion"""

    def name(self) -> Text:
        return "action_confirm_delete"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="Which emails would you like to delete? Please be specific.")
        return []


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

        dispatcher.utter_message(
            text="What changes would you like to make to the draft?")
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
        dispatcher.utter_message(
            text=f"Are you ready to send this email to {recipient}?")
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

        dispatcher.utter_message(
            text="Your draft has been saved. You can access it later to continue editing or send it.")
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

        dispatcher.utter_message(
            text="Are you sure you want to discard this draft? This action cannot be undone.")
        return []


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

        dispatcher.utter_message(
            text="Which sender's emails are you looking for?")
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

        dispatcher.utter_message(
            text="What subject or keywords are you looking for in the email subject line?")
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

        dispatcher.utter_message(
            text="What date or date range are you looking for? (e.g., today, last week, between June 1-15, etc.)")
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

        dispatcher.utter_message(
            text="What words or phrases are you looking for in the email body?")
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

        dispatcher.utter_message(
            text="What type of attachment are you looking for? (e.g., PDF, images, spreadsheets)")
        return []


class ActionCALMProcessor(Action):
    """Action for CALM processing for fallback handling"""

    def name(self) -> Text:
        return "action_calm_processor"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # In a real implementation, this would call the CALM processor with the
        # appropriate system prompts based on the active flow
        active_flow = tracker.get_slot("active_flow") or "main_flow"

        # In this simplified example, we just send a message
        dispatcher.utter_message(
            text=f"I'm not sure I understood that correctly. We're currently in the {active_flow} flow. Could you please rephrase or provide more details?")

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
        dispatcher.utter_message(
            text="Searching for emails matching your criteria...")
        dispatcher.utter_message(
            text="(This is a simulation - in a real implementation, this would search your actual emails)")

        # Return a sample response
        dispatcher.utter_message(
            text="I found 5 emails matching your search criteria. Would you like to refine your search or view any of these emails?")

        return []


class ActionOrganizeInbox(Action):
    """Action to organize inbox based on criteria"""

    def name(self) -> Text:
        return "action_organize_inbox"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # This would connect to an email service in a real implementation
        dispatcher.utter_message(
            text="Organizing your inbox based on your preferences...")
        dispatcher.utter_message(
            text="(This is a simulation - in a real implementation, this would organize your actual emails)")

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

        recipient = tracker.get_slot("email_recipient") or "the recipient"
        subject = tracker.get_slot("email_subject") or "the subject"

        dispatcher.utter_message(
            text=f"Drafting an email to {recipient} with subject '{subject}'...")
        dispatcher.utter_message(
            text="(This is a simulation - in a real implementation, this would create an actual email draft)")

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

        recipient = tracker.get_slot("email_recipient") or "the recipient"

        dispatcher.utter_message(
            text=f"Your email has been sent to {recipient}.")
        dispatcher.utter_message(
            text="(This is a simulation - in a real implementation, this would send an actual email)")

        return []


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
            dispatcher.utter_message(
                "I don't see any recent emails to show you.")
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
            dispatcher.utter_message(
                text="You don't have any new emails at the moment.")

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
            {"id": 2, "subject": "Project update",
                "sender": "manager@example.com"},
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
            email_list = "\n".join(
                [f"- {e['id']}: {e['subject']} from {e['sender']}" for e in emails])
            dispatcher.utter_message(
                text=f"Here are your emails:\n{email_list}")
        else:
            dispatcher.utter_message(text="No emails to display.")

        return []


class ActionPostReadOptions(Action):
    def name(self) -> Text:
        return "action_post_read_options"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="Would you like to reply to this email, forward it, archive it, or delete it?")
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

        dispatcher.utter_message(
            text=f"I've drafted your email:\n\n{email_preview}")
        return []


class ActionCollectDraftInfo(Action):
    def name(self) -> Text:
        return "action_collect_draft_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Check if we already have recipient information
        recipient = tracker.get_slot("email_recipient")

        if not recipient:
            dispatcher.utter_message(
                text="Who would you like to send this email to?")
            return []

        # Check if we have subject information
        subject = tracker.get_slot("email_subject")

        if not subject:
            dispatcher.utter_message(
                text="What should be the subject of your email?")
            return []

        return []
