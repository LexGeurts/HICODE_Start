/**
 * MailoBot Database Configuration
 */
(function () {
    // Initialize Dexie
    const db = new Dexie('mailobot-hackathon');

    // Define database schema
    db.version(1).stores({
        conversations: '++id, timestamp, sender, message, context',
        imapSettings: 'id, host, port, username, password, tls',
        emails: '++id, messageId, from, to, subject, body, timestamp, read, folder, attachments'
    });

    /**
     * Save a conversation to the database
     * @param {Object} conversationData - Conversation data to save
     * @returns {Promise} - Promise that resolves with the new conversation ID
     */
    async function saveConversation(conversationData) {
        try {
            const id = await db.conversations.add({
                ...conversationData,
                timestamp: new Date().toISOString()
            });
            console.log(`Conversation saved with ID: ${id}`);
            return id;
        } catch (error) {
            console.error('Error saving conversation:', error);
            throw error;
        }
    }

    /**
     * Get all conversations
     * @returns {Promise} - Promise that resolves with an array of conversations
     */
    async function getConversations() {
        try {
            return await db.conversations.toArray();
        } catch (error) {
            console.error('Error fetching conversations:', error);
            throw error;
        }
    }

    /**
     * Save IMAP settings to the database and to a JSON file on the server
     * @param {Object} settings - IMAP settings
     * @returns {Promise} - Promise that resolves when settings are saved
     */
    async function saveImapSettings(settings) {
        try {
            // Always use id=1 for the single settings record
            settings.id = 1;
            await db.imapSettings.put(settings);
            
            // Also save settings to a server-side JSON file
            await saveImapSettingsToServer(settings);
            
            console.log('IMAP settings saved to database and server');
        } catch (error) {
            console.error('Error saving IMAP settings:', error);
            throw error;
        }
    }

    /**
     * Save IMAP settings to a server-side JSON file
     * @param {Object} settings - IMAP settings
     * @returns {Promise} - Promise that resolves when settings are saved to the server
     */
    async function saveImapSettingsToServer(settings) {
        try {
            // Remove the id field as it's not needed in the JSON file
            const settingsToSave = { ...settings };
            delete settingsToSave.id;
            
            const response = await fetch('/api/save_imap_settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settingsToSave)
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error saving IMAP settings to server:', error);
            throw error;
        }
    }

    /**
     * Get IMAP settings from the database
     * @returns {Promise} - Promise that resolves with the IMAP settings
     */
    async function getImapSettings() {
        try {
            return await db.imapSettings.get(1);
        } catch (error) {
            console.error('Error fetching IMAP settings:', error);
            throw error;
        }
    }

    /**
     * Save an email to the database
     * @param {Object} emailData - Email data to save
     * @returns {Promise} - Promise that resolves with the new email ID
     */
    async function saveEmail(emailData) {
        try {
            // If email with this messageId already exists, update it instead of adding new
            let existingEmail = null;
            
            if (emailData.messageId) {
                existingEmail = await db.emails
                    .where('messageId')
                    .equals(emailData.messageId)
                    .first();
            }
            
            if (existingEmail) {
                // Update existing email
                const updatedEmail = {
                    ...existingEmail,
                    ...emailData,
                    id: existingEmail.id // Keep the same ID
                };
                
                await db.emails.update(existingEmail.id, updatedEmail);
                console.log(`Email updated with ID: ${existingEmail.id}`);
                return existingEmail.id;
            } else {
                // Create new email
                const id = await db.emails.add({
                    ...emailData,
                    timestamp: emailData.timestamp || new Date().toISOString()
                });
                console.log(`Email saved with ID: ${id}`);
                return id;
            }
        } catch (error) {
            console.error('Error saving email:', error);
            throw error;
        }
    }

    /**
     * Get emails from the database
     * @param {Object} options - Options for filtering emails
     * @returns {Promise} - Promise that resolves with an array of emails
     */
    async function getEmails(options = {}) {
        try {
            let query = db.emails;
            
            // Filter by folder if specified
            if (options.folder) {
                query = query.where('folder').equals(options.folder);
            }
            
            // Filter by read/unread status if specified
            if (options.read !== undefined) {
                query = query.filter(email => email.read === options.read);
            }
            
            // Sort by timestamp (newest first)
            const emails = await query.toArray();
            return emails.sort((a, b) => {
                return new Date(b.timestamp) - new Date(a.timestamp);
            });
        } catch (error) {
            console.error('Error fetching emails:', error);
            throw error;
        }
    }

    /**
     * Mark email as read
     * @param {number} emailId - ID of the email to mark as read
     * @returns {Promise} - Promise that resolves when the operation is complete
     */
    async function markEmailAsRead(emailId) {
        try {
            await db.emails.update(emailId, { read: true });
            console.log(`Email ${emailId} marked as read`);
            return true;
        } catch (error) {
            console.error('Error marking email as read:', error);
            throw error;
        }
    }

    /**
     * Search emails
     * @param {Object} criteria - Search criteria
     * @returns {Promise} - Promise that resolves with matching emails
     */
    async function searchEmails(criteria) {
        try {
            return await db.emails
                .filter(email => {
                    let match = true;
                    
                    if (criteria.from) {
                        match = match && email.from.toLowerCase().includes(criteria.from.toLowerCase());
                    }
                    
                    if (criteria.subject) {
                        match = match && email.subject.toLowerCase().includes(criteria.subject.toLowerCase());
                    }
                    
                    if (criteria.text) {
                        const text = criteria.text.toLowerCase();
                        const subjectMatch = email.subject.toLowerCase().includes(text);
                        const bodyMatch = email.body.toLowerCase().includes(text);
                        match = match && (subjectMatch || bodyMatch);
                    }
                    
                    return match;
                })
                .toArray();
        } catch (error) {
            console.error('Error searching emails:', error);
            throw error;
        }
    }

    // Export functions to global scope to ensure they're accessible
    window.mailoDB = {
        saveConversation,
        getConversations,
        saveImapSettings,
        getImapSettings,
        saveEmail,
        getEmails,
        markEmailAsRead,
        searchEmails,
        db
    };

    // Log that initialization is complete
    console.log('MailoDB initialized successfully');
})();
