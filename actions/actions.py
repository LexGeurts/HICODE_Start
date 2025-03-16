"""
Main actions file that imports all actions from modules
"""
# Import required modules
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

# Import all actions from modules
from .flow_control import ActionActivateFlow
from .email_management import (
    ActionCollectFolderInfo,
    ActionCollectFilterCriteria, 
    ActionMarkEmailsRead,
    ActionConfirmDelete, 
    ActionOrganizeInbox
)
from .email_drafting import (
    ActionCollectEdits,
    ActionConfirmSend,
    ActionSaveDraft,
    ActionConfirmDiscard,
    ActionDraftEmail,
    ActionSendEmail,
    ActionDraftComplete,
    ActionCollectDraftInfo,
    ActionReplyToEmail
)
from .email_search import (
    ActionCollectSender,
    ActionCollectSubject,
    ActionCollectDate,
    ActionCollectContent,
    ActionCollectAttachment,
    ActionSearchEmails
)
from .email_read import (
    ActionCheckEmails,
    ActionReadEmail,
    ActionShowInbox,
    ActionShowSettings,
    ActionReadRecentEmail,
    ActionNotifyNewEmails,
    ActionFetchEmails,
    ActionDisplayEmailList,
    ActionPostReadOptions
)
from .fallback import (
    ActionCALMProcessor,
    ActionProcessRephrased
)

# Export all actions (central import for custom actions; adjust as needed)
__all__ = [
    'ActionActivateFlow',
    'ActionCollectFolderInfo',
    'ActionCollectFilterCriteria',
    'ActionMarkEmailsRead',
    'ActionConfirmDelete',
    'ActionCollectEdits',
    'ActionConfirmSend',
    'ActionSaveDraft',
    'ActionConfirmDiscard',
    'ActionCollectSender',
    'ActionCollectSubject',
    'ActionCollectDate',
    'ActionCollectContent',
    'ActionCollectAttachment',
    'ActionCALMProcessor',
    'ActionProcessRephrased',
    'ActionSearchEmails',
    'ActionOrganizeInbox',
    'ActionDraftEmail',
    'ActionSendEmail',
    'ActionCheckEmails',
    'ActionReadEmail',
    'ActionShowInbox',
    'ActionShowSettings',
    'ActionReadRecentEmail',
    'ActionNotifyNewEmails',
    'ActionFetchEmails',
    'ActionDisplayEmailList',
    'ActionPostReadOptions',
    'ActionDraftComplete',
    'ActionCollectDraftInfo',
    'ActionReplyToEmail'
]
