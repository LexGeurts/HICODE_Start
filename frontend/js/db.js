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
     * Save email to the database
     * @param {Object} emailData - Email data to save
     * @returns {Promise} - Promise that resolves with the new email ID
     */
    async function saveEmail(emailData) {
        try {
            const id = await db.emails.add({
                ...emailData,
                timestamp: emailData.timestamp || new Date().toISOString(),
                read: emailData.read || false
            });
            console.log(`Email saved with ID: ${id}`);
            return id;
        } catch (error) {
            console.error('Error saving email:', error);
            throw error;
        }
    }

    /**
     * Get emails from the database
     * @param {Object} filter - Filter criteria
     * @returns {Promise} - Promise that resolves with an array of emails
     */
    async function getEmails(filter = {}) {
        try {
            let collection = db.emails;

            if (filter.folder) {
                collection = collection.where('folder').equals(filter.folder);
            }

            if (filter.read !== undefined) {
                collection = collection.where('read').equals(filter.read);
            }

            return await collection.reverse().sortBy('timestamp');
        } catch (error) {
            console.error('Error fetching emails:', error);
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
        db
    };

    // Log that initialization is complete
    console.log('MailoDB initialized successfully');
})();
