import json
import os
import base64
import datetime
import requests

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from jinja2 import Template

# Import EmailMCP
from utils.email_mcp import EmailMCP

# Import OpenAI utilities 
try:
    from utils.openai_utils import OpenAIClient
except ImportError:
    # Fallback if OpenAI utils aren't available
    import os
    import requests
    
    class OpenAIClient:
        """Basic fallback implementation if the main OpenAI utils aren't available"""
        def __init__(self, config_path=None):
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.base_url = "https://api.openai.com/v1"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }


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


def make_json_serializable(obj):
    """Convert any non-serializable objects to serializable types recursively."""
    if isinstance(obj, bytes):
        # Convert bytes to base64 encoded string
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        # For other types, convert to string
        return str(obj)
    
class ActionCheckEmail(Action):
    def name(self) -> Text:
        return "action_check_emails"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Get an initialized email client with settings from the JSON file"""
        imap_settings = load_imap_settings()

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
            
            folder = "INBOX"
            limit = 5

            if connected:
                # Select folder
                mcp.select_folder(folder)

                # Get unread count
                unread_count = mcp.get_unread_count()

                # Get unread emails
                emails = mcp.get_unread_emails(limit=limit)

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
                        response = f"I found {len(emails)} unread emails in your {folder} folder, but no unread emails."
                else:
                    response = f"I checked your {folder} folder, but didn't find any unread emails."
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
        
        # Make context and emails JSON serializable by converting any bytes to strings
        serializable_context = make_json_serializable(context)
        
        # Add a custom message with the action and context information
        # This is what the frontend looks for in handleRasaAction
        action_data = {
            "name": "check_email",
        }
        
        # Only add these fields if they were successfully retrieved
        if serializable_context.get("connected", False):
            action_data["unread_count"] = serializable_context.get("unread_count", 0)
            action_data["emails"] = serializable_context.get("emails", [])
            
        dispatcher.utter_message(
            json_message={
                "action": action_data,
                "context": serializable_context
            }
        )

        # Update slots - make sure context is serializable
        return [
            SlotSet("mcp_context", serializable_context),
            SlotSet("email_connected", serializable_context.get("connected", False)),
            SlotSet("emails", serializable_context.get("emails", [])),
            SlotSet("has_emails", len(serializable_context.get("emails", [])) > 0)
        ]


class ActionTestEmailConnection(Action):
    def name(self) -> Text:
        return "action_test_email_connection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Get an initialized email client with settings from the JSON file"""
        imap_settings = load_imap_settings()

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
                    if (unread > 0):
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
            
        try:
            # Load email settings if needed to fetch from server
            imap_settings = load_imap_settings()
            
            # This will be used if we implement fetching directly from server
            # For now, we'll let the frontend handle the retrieval from Dexie
            
            # Send a response with action information for the frontend
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
            
        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I encountered an error retrieving that email: {str(e)}")
            return []

class ActionSearchEmails(Action):
    def name(self) -> Text:
        return "action_search_emails"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get search terms
        search_term = tracker.get_slot("search_term")
        sender = tracker.get_slot("sender")
        subject = tracker.get_slot("subject")
        
        metadata = tracker.get_latest_message().get("metadata", {})
        if metadata.get("searchTerm"):
            search_term = metadata.get("searchTerm")
        if metadata.get("sender"):
            sender = metadata.get("sender")
        if metadata.get("subject"):
            subject = metadata.get("subject")
            
        # Default response if no search criteria
        if not any([search_term, sender, subject]):
            dispatcher.utter_message(text="Please provide a search term, sender name, or subject to search for emails.")
            return []
            
        try:
            # Build search criteria dict
            search_criteria = {}
            if search_term:
                search_criteria["text"] = search_term
            if sender:
                search_criteria["from"] = sender
            if subject:
                search_criteria["subject"] = subject
                
            # Load settings
            imap_settings = load_imap_settings()
            
            # For now, we'll let the frontend do the search
            # Just send the search criteria
            dispatcher.utter_message(
                json_message={
                    "action": {
                        "name": "search_emails",
                        "criteria": search_criteria
                    },
                    "context": {
                        "search_criteria": search_criteria
                    }
                }
            )
            
            return [
                SlotSet("search_criteria", search_criteria),
                SlotSet("search_term", search_term),
                SlotSet("sender", sender),
                SlotSet("subject", subject)
            ]
            
        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I encountered an error searching for emails: {str(e)}")
            return []

class ActionSaveDraft(Action):
    def name(self) -> Text:
        return "action_save_draft"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Save email to draft when recipient, subject, and content slots are collected"""
        
        # Get email details from slots
        recipient = tracker.get_slot("recipient")
        subject = tracker.get_slot("subject")
        content = tracker.get_slot("content")
        
        # Debug info - print the slot values
        print(f"Debug - Slots: recipient='{recipient}', subject='{subject}', content='{content}'")
        
        # Check if we have the minimum required information
        # At least recipient and subject are required
        if not recipient or not subject:
            dispatcher.utter_message(text="I couldn't save your draft. Please make sure you've provided both a recipient and subject.")
            return [SlotSet("draft_saved", False)]
        
        # If content is None, set it to an empty string
        if content is None:
            content = ""
            print("Setting empty content for draft")
        
        try:
            # Create a draft email object
            draft_email = {
                "to": recipient,
                "subject": subject,
                "body": content or "",  # Use empty string if content is None
                "timestamp": str(datetime.datetime.now().isoformat()),
                "draft": True
            }
            
            # Load current user email from settings if available
            imap_settings = load_imap_settings()
            if imap_settings and "username" in imap_settings:
                draft_email["from"] = imap_settings["username"]
            
            # Initialize MCP and try to save to IMAP server
            saved_to_imap = False
            save_error = None
            
            try:
                if imap_settings:
                    mcp = EmailMCP(imap_settings)
                    if mcp.connect():
                        saved_to_imap = mcp.save_draft(draft_email)
                        if not saved_to_imap:
                            save_error = mcp.get_context().get('error', 'Unknown error')
                        mcp.disconnect()
            except Exception as e:
                save_error = str(e)
                print(f"Error saving draft to IMAP: {e}")
            
            # Send draft to frontend regardless of IMAP result
            dispatcher.utter_message(text=f"I've saved your draft email to {recipient} with subject: {subject}" + 
                                    (". It's also been saved to your email drafts folder." if saved_to_imap else ""))
            
            if save_error:
                dispatcher.utter_message(text=f"Note: I couldn't save to your email provider's drafts folder. {save_error}")
            
            # Send a custom message for the frontend to handle
            dispatcher.utter_message(
                json_message={
                    "action": {
                        "name": "save_draft",
                        "draft_email": draft_email,
                        "saved_to_imap": saved_to_imap
                    },
                    "context": {
                        "draft_email": draft_email,
                        "draft_saved_to_imap": saved_to_imap,
                        "save_error": save_error
                    }
                }
            )
            
            return [
                SlotSet("draft_email", draft_email),
                SlotSet("draft_saved", True),
                SlotSet("draft_saved_to_imap", saved_to_imap)
            ]
            
        except Exception as e:
            print(f"Error saving draft: {str(e)}")
            dispatcher.utter_message(text=f"Sorry, I encountered an error saving your draft: {str(e)}")
            return [SlotSet("draft_saved", False)]

class ActionSendEmail(Action):
    def name(self) -> Text:
        return "action_send_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Send an email using the collected recipient, subject, and content slots"""
        
        # Get email details from slots
        recipient = tracker.get_slot("recipient")
        subject = tracker.get_slot("subject")
        content = tracker.get_slot("content")
        
        # Debug info - print the slot values
        print(f"Debug - Sending email: recipient='{recipient}', subject='{subject}', content='{content}'")
        
        # Check if we have all required information
        if not recipient or not subject:
            dispatcher.utter_message(text="I couldn't send your email. Please make sure you've provided a recipient and subject.")
            return [SlotSet("email_sent", False)]
        
        # If content is None, set it to an empty string
        if content is None:
            content = ""
            print("Setting empty content for sending email")
        
        try:
            # Load current user email from settings
            imap_settings = load_imap_settings()
            if not imap_settings:
                dispatcher.utter_message(text="I couldn't send your email because your email settings aren't configured.")
                return [SlotSet("email_sent", False)]
                
            # Create an email object
            email_data = {
                "to": recipient,
                "subject": subject,
                "body": content,
                "timestamp": str(datetime.datetime.now().isoformat()),
                "from": imap_settings["username"] if imap_settings and "username" in imap_settings else ""
            }
            
            # Initialize MCP and send the email
            sent_success = False
            send_error = None
            
            try:
                mcp = EmailMCP(imap_settings)
                sent_success = mcp.send_email(email_data)
                if not sent_success:
                    send_error = mcp.get_context().get('error', 'Unknown error')
            except Exception as e:
                send_error = str(e)
                print(f"Error sending email: {e}")
            
            # Send response to user based on success/failure
            if sent_success:
                dispatcher.utter_message(text=f"I've sent your email to {recipient} with subject: {subject}")
            else:
                dispatcher.utter_message(
                    text=f"I couldn't send your email. {send_error if send_error else 'Please check your email settings and try again.'}"
                )
            
            # Send a custom message for the frontend to handle
            dispatcher.utter_message(
                json_message={
                    "action": {
                        "name": "send_email",
                        "email_data": email_data,
                        "success": sent_success
                    },
                    "context": {
                        "email_data": email_data,
                        "email_sent": sent_success,
                        "send_error": send_error
                    }
                }
            )
            
            # Clear the slots after sending
            return [
                SlotSet("email_sent", sent_success),
                SlotSet("send_error", send_error),
                SlotSet("recipient", None if sent_success else recipient),
                SlotSet("subject", None if sent_success else subject),
                SlotSet("content", None if sent_success else content)
            ]
            
        except Exception as e:
            print(f"Error in action_send_email: {str(e)}")
            dispatcher.utter_message(text=f"Sorry, I encountered an error sending your email: {str(e)}")
            return [SlotSet("email_sent", False)]

class ActionGenerateDraft(Action):
    def name(self) -> Text:
        return "action_generate_draft"

    def get_prompt_template(self) -> Text:
        """Load the email draft prompt template from file."""
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_path = os.path.join(current_dir, 'prompts', 'email-draft-prompt.jinja2')
            
            if os.path.exists(template_path):
                with open(template_path, 'r') as file:
                    return file.read()
            else:
                print(f"Warning: Email draft prompt template not found at {template_path}")
                # Fallback to a basic template
                return """You are an AI email assistant.
                Draft an email with subject: {{ subject }}, in a {{ tone }} tone.
                {% if email_thread %}Based on this thread: {{ email_thread }}{% endif %}
                ONLY RETURN THE DRAFT TEXT."""
        except Exception as e:
            print(f"Error loading prompt template: {e}")
            return "Write an email draft about {{ subject }} in a {{ tone }} tone."

    def call_openai_api(self, prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 800) -> str:
        """Make a direct call to OpenAI API"""
        try:
            # First try using our OpenAI utility class if available
            try:
                # Create OpenAI client with no config path - it will use the absolute path internally
                openai_client = OpenAIClient()
                # Use draft_generator model if defined in config
                model_to_use = openai_client.config['models'].get('draft_generator', model)
                
                print(f"Using OpenAI model: {model_to_use}")
                
                # Call OpenAI via the utility
                return openai_client.generate_text(
                    prompt=prompt,
                    model=model_to_use
                )
            except Exception as e:
                print(f"OpenAI utility error: {e}")
                
                # Fall back to direct API call
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set")
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                url = "https://api.openai.com/v1/chat/completions"
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an AI email assistant tasked with drafting professional emails."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                print("Falling back to direct OpenAI API call")
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                else:
                    raise ValueError("No content in OpenAI response")
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Generate an email draft based on subject, tone, and optional context."""
        
        # Get required slots
        subject = tracker.get_slot("subject")
        tone = tracker.get_slot("tone") or "professional"  # Default to professional
        recipient = tracker.get_slot("recipient")
        
        # Get optional slots and context
        current_email_id = tracker.get_slot("current_email_id")
        email_thread = tracker.get_slot("email_thread")
        additional_instructions = tracker.get_slot("additional_instructions")
        
        # Check for required slots
        if not subject:
            dispatcher.utter_message(text="I need a subject to draft an email. What's the email about?")
            return [SlotSet("auto_draft", False)]
        
        # Debug info
        print(f"Generating draft with subject='{subject}', tone='{tone}', recipient='{recipient}'")
        print(f"Additional context: current_email_id='{current_email_id}', has_thread={email_thread is not None}")
        
        # Prepare variables for prompt
        variables = {
            "subject": subject,
            "tone": tone,
            "recipient": recipient,
            "email_thread": email_thread,
            "additional_instructions": additional_instructions
        }
        
        try:
            # Get prompt template
            template_text = self.get_prompt_template()
            
            # Render the template with variables
            template = Template(template_text)
            rendered_prompt = template.render(**variables)
            
            # Call OpenAI
            generated_content = self.call_openai_api(rendered_prompt)
            
            # Set the generated content to the content slot
            if generated_content:
                clean_content = self.clean_generated_text(generated_content)
                
                # First, inform the user that we've created a draft
                dispatcher.utter_message(text=f"I've drafted an email about '{subject}' in a {tone} tone.")
                
                # Create a markdown-formatted draft preview
                markdown_draft = f"""
                **📝 Email Draft Preview**
                **To:** {recipient or "[Recipient]"}
                **Subject:** {subject}
                **Tone:** {tone}

                {clean_content}
                """
                
                # Send the markdown preview of the email draft
                dispatcher.utter_message(text=markdown_draft)
                
                # Also send a custom JSON message for the frontend
                dispatcher.utter_message(
                    json_message={
                        "action": {
                            "name": "show_draft",
                            "draft": {
                                "subject": subject,
                                "content": clean_content,
                                "tone": tone,
                                "recipient": recipient
                            }
                        },
                        "context": {
                            "generated_draft": clean_content,
                            "draft_subject": subject,
                            "content": clean_content  # Include in context for consistency
                        }
                    }
                )
                
                # Return SlotSet actions to update the slots
                return [
                    SlotSet("content", clean_content),
                    SlotSet("auto_draft", True),
                    SlotSet("draft_generated", True)
                ]
            else:
                dispatcher.utter_message(text="I couldn't generate an email draft. Let's create one together step by step.")
                return [
                    SlotSet("auto_draft", False),
                    SlotSet("draft_generated", False)
                ]
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error generating draft: {error_msg}")
            dispatcher.utter_message(text=f"Sorry, I encountered an error generating your draft: {error_msg}")
            return [
                SlotSet("auto_draft", False),
                SlotSet("draft_generated", False)
            ]
    
    def clean_generated_text(self, text: str) -> str:
        """Clean the generated text by removing unnecessary elements."""
        if not text:
            return ""
            
        # Debug original text
        print(f"Original draft text ({len(text)} chars):\n{text[:100]}...")
            
        # Remove typical LLM explanations or formatting
        lines = text.strip().split('\n')
            
        # Track if we've found content markers
        content_lines = []
        capture = False
        
        # Markers for explanatory content we want to skip
        skip_markers = [
            "here's a draft", "here is a draft", "draft email", "email draft", 
            "subject:", "to:", "from:", "draft for you", "here is the", "here's the"
        ]
        
        # Process each line
        for i, line in enumerate(lines):
            lower_line = line.lower().strip()
            
            # Skip empty lines at the beginning
            if not content_lines and not lower_line:
                continue
                
            # Check if this line contains a skip marker
            should_skip = False
            is_header = False
            
            if i < 5:  # Only check first few lines for efficiency
                should_skip = any(marker in lower_line for marker in skip_markers)
                is_header = lower_line.startswith("subject:") or lower_line.startswith("to:") or lower_line.startswith("from:")
            
            if should_skip:
                if is_header:
                    # Skip email header lines
                    continue
                else:
                    # This is a marker line, start capturing from next line
                    capture = True
                    continue
            
            # Always capture content once we've started or if no markers found
            if capture or len(content_lines) > 0 or i > 2:  # Start capturing after line 2 if nothing captured yet
                content_lines.append(line)
        
        # If we didn't capture anything meaningful, return the original text with minimal cleaning
        if not content_lines:
            print("No content captured! Using original text with minimal cleaning")
            # Skip first line if it looks like an explanation, otherwise use full text
            if len(lines) > 1 and any(marker in lines[0].lower() for marker in skip_markers):
                result = '\n'.join(lines[1:])
            else:
                result = '\n'.join(lines)
        else:
            # Join captured lines
            result = '\n'.join(content_lines)
            
        # Debug cleaned text
        print(f"Cleaned draft text ({len(result)} chars):\n{result[:100]}...")
        return result