/**
 * MailoBot Email Service
 * Handles background email checking and processing with MCP integration
 */

// Configuration
const EMAIL_CHECK_INTERVAL = 60000; // 1 minute
const RASA_SERVER_URL = 'http://localhost:5005'; // Rasa server URL
const USE_SIMULATION = false; // Set to false in production, true for demo

// For simulation only
const SIMULATION_PROBABILITY = 0.2; // 20% chance of generating emails in demo mode

(function () {
    class EmailService {
        constructor() {
            this.isRunning = false;
            this.checkInterval = null;
            this.lastCheckTime = null;
            this.newEmailCallbacks = [];
            this.connected = false;
            this.connectionStatus = "disconnected";

            // For simulation only
            this.emailSenders = ['team@github.com', 'support@notion.so', 'newsletter@medium.com', 'updates@linkedin.com', 'no-reply@spotify.com'];
            this.emailSubjects = [
                'Your weekly digest',
                'Important account notification',
                'Meeting invitation',
                'Payment receipt',
                'New feature announcement',
                'Security alert',
                'Project update',
                'Subscription renewal'
            ];

            // MCP email-related properties
            this.unreadCount = 0;
            this.emailFolders = ['inbox', 'sent', 'drafts', 'trash'];
            this.currentFolder = 'inbox';

            // Set up Rasa custom action handler
            this.setupRasaActionHandler();

            // Debug mode for troubleshooting
            this.debugMode = true;
        }

        /**
         * Set up a handler for custom actions from Rasa
         */
        setupRasaActionHandler() {
            // Listen for custom message events from Rasa service
            window.addEventListener('rasa-custom-action', (event) => {
                if (event.detail && event.detail.action) {
                    this.handleRasaAction(event.detail.action, event.detail.context);
                }
            });
        }

        /**
         * Handle custom actions from Rasa
         * @param {Object} action - The action object from Rasa
         * @param {Object} context - The context object from Rasa
         */
    handleRasaAction(action, context) {
        console.log('Received Rasa action:', action.name, action);

        switch (action.name) {
            case 'check_email':
                // Update connection status from MCP
                if (context && context.connected !== undefined) {
                    this.connected = context.connected;
                    this.connectionStatus = this.connected ? "connected" : "disconnected";
                    console.log(`Email connection status updated: ${this.connectionStatus}`);
                }

                // Update unread count if provided
                if (action.unread_count !== undefined) {
                    this.unreadCount = action.unread_count;
                    console.log(`Updated unread count: ${this.unreadCount}`);
                } else if (context && context.unread_count !== undefined) {
                    this.unreadCount = context.unread_count;
                    console.log(`Updated unread count from context: ${this.unreadCount}`);
                }

                // Process recent emails if provided in either action or context
                let recentEmails = [];

                // Try different field names to be resilient to format changes
                if (action.emails && Array.isArray(action.emails)) {
                    console.log('Found emails in action:', action.emails.length);
                    recentEmails = action.emails;
                } else if (context && context.recent_emails && Array.isArray(context.recent_emails)) {
                    console.log('Found recent_emails in context:', context.recent_emails.length);
                    recentEmails = context.recent_emails;
                } else if (context && context.emails && Array.isArray(context.emails)) {
                    console.log('Found emails in context:', context.emails.length);
                    recentEmails = context.emails;
                }

                if (this.debugMode) {
                    console.log('Recent emails to process:', recentEmails.length);
                    if (recentEmails.length > 0) {
                        console.log('First email sample:', recentEmails[0]);
                    }
                }

                // Process each email
                if (recentEmails.length > 0) {
                    console.log(`Processing ${recentEmails.length} recent emails`);
                    
                    recentEmails.forEach(email => {
                        try {
                            const formattedEmail = this.formatMCPEmail(email);
                            console.log('Formatted email:', formattedEmail);
                            
                            // Save to DB and notify
                            this.saveAndNotifyEmail(formattedEmail);
                        } catch (error) {
                            console.error('Error processing email:', error, email);
                        }
                    });
                    
                    // Dispatch a custom event that new emails were processed
                    window.dispatchEvent(new CustomEvent('emails-processed', { 
                        detail: { count: recentEmails.length } 
                    }));
                }

                // Display email check results if this isn't a silent check
                if (!action.silent && window.addSystemMessageToChat) {
                    let message = "I've checked your emails.";
                    
                    if (this.unreadCount > 0) {
                        message = `I've checked your emails. You have ${this.unreadCount} unread messages.`;
                    } else {
                        message = "I've checked your emails. You have no new messages.";
                    }
                    
                    window.addSystemMessageToChat(message);
                }
                break;

                case 'email_notification':
                    // Handle notification about new emails from background checker
                    if (action.emails && Array.isArray(action.emails)) {
                        action.emails.forEach(email => {
                            // Save to DB and notify
                            this.saveAndNotifyEmail(email);
                        });
                    }
                    break;

                case 'read_email':
                    // Mark email as read in DB
                    if (action.emailId) {
                        this.markEmailAsRead(action.emailId);
                    }
                    break;

                case 'delete_email':
                    // Delete email from DB
                    if (action.emailId) {
                        this.deleteEmail(action.emailId);
                    }
                    break;

                case 'test_connection':
                    // Handle connection test result
                    if (context && context.connected !== undefined) {
                        this.connected = context.connected;
                        this.connectionStatus = this.connected ? "connected" : "disconnected";

                        // Dispatch custom event for UI to update
                        const event = new CustomEvent('email-connection-test', {
                            detail: {
                                success: context.connected,
                                error: context.error || null
                            }
                        });
                        window.dispatchEvent(event);
                    }
                    break;

                default:
                    console.log('Unknown Rasa action:', action.name);
            }
        }

        /**
         * Start the background email checking service
         */
        start() {
            if (this.isRunning) {
                console.log('Email service is already running');
                return;
            }

            console.log('Starting email service...');
            this.isRunning = true;

            // Immediately check for emails
            // this.checkEmails();

            // Set up interval for checking emails
            this.checkInterval = setInterval(() => {
                this.checkEmails();
            }, EMAIL_CHECK_INTERVAL);
        }

        /**=
         * Stop the background email checking service
         */
        stop() {
            if (!this.isRunning) {
                return;
            }

            console.log('Stopping email service...');
            clearInterval(this.checkInterval);
            this.isRunning = false;
        }

        /**
         * Check for new emails using IMAP settings from Dexie.js
         * This will send the settings to the MCP bridge through Rasa
         */
        async checkEmails() {
            try {
                // Make sure mailoDB is available
                if (!window.mailoDB) {
                    console.error('mailoDB is not initialized. Email checking skipped.');
                    return;
                }

                // Get IMAP settings from Dexie.js
                const settings = await window.mailoDB.getImapSettings();
                if (!settings) {
                    console.log('No IMAP settings found. Email checking skipped.');
                    return;
                }

                // Check if Rasa server is available before attempting to send email check
                const isRasaAvailable = await this.checkRasaAvailability();
                if (!isRasaAvailable) {
                    console.warn('Rasa server is not available. Email checking skipped.');
                    return null;
                }

                console.log('Checking for new emails...');
                this.lastCheckTime = new Date();

                // Send check email request to Rasa with IMAP settings
                const response = await this.sendCheckEmailRequest(settings, {
                    folder: this.currentFolder,
                    limit: 10
                });

                // Add chat notification about the check
                if (response && window.addSystemMessageToChat) {
                    // Only notify if this is not triggered by the user explicitly asking
                    if (!this.userInitiatedCheck) {
                        const timestamp = new Date();
                        let message = "I've checked your emails.";
                        
                        if (response.unread_count && response.unread_count > 0) {
                            message = `I've checked your emails. You have ${response.unread_count} unread messages.`;
                        }
                        
                        window.addSystemMessageToChat(message, timestamp);
                    }
                    // Reset the flag
                    this.userInitiatedCheck = false;
                }

                return response;
            } catch (error) {
                console.error('Error checking emails:', error);
                return null;
            }
        }

        /**
         * Check if the Rasa server is available
         * @returns {Promise<boolean>} - Promise resolving to true if Rasa is available
         */
        async checkRasaAvailability() {
            try {
                const response = await fetch('/api/check_rasa');
                if (!response.ok) {
                    return false;
                }
                const data = await response.json();
                return data.status === 'available';
            } catch (error) {
                console.error('Error checking Rasa availability:', error);
                return false;
            }
        }

        /**
         * Send a request to Rasa to check emails using MCP
         * @param {Object} settings - IMAP settings from Dexie.js
         * @param {Object} options - Additional options like folder, limit, etc.
         */
        async sendCheckEmailRequest(settings, options = {}) {
            try {
                const requestOptions = {
                    folder: this.currentFolder,
                    limit: 10,
                    ...options
                };

                const response = await fetch('/api/rasa_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: "check my emails",
                        context: {
                            imap_settings: settings,
                            action: "check_email",
                            options: requestOptions,
                            email_limit: requestOptions.limit
                        }
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
                }

                const data = await response.json();

                // If there's an error but the server responded with a valid JSON
                if (data.error) {
                    console.warn('Server returned error:', data.error);
                    // The context is still returned even on error
                    return data;
                }

                // Set flag if this was initiated by user request vs background check
                if (options.userInitiated) {
                    this.userInitiatedCheck = true;
                }

                return data;
            } catch (error) {
                console.error('Error sending check email request to Rasa:', error);

                // Return a minimal valid response to avoid breaking the app
                return {
                    messages: [],
                    context: {
                        connected: false,
                        error: error.message,
                        emails: []
                    },
                    actions: []
                };
            }
        }

        /**
         * Test IMAP connection with given settings
         * @param {Object} settings - IMAP settings to test
         * @returns {Promise<boolean>} - Promise resolving to connection result
         */
        async testConnection(settings) {
            try {
                // First check if Rasa is available
                const isRasaAvailable = await this.checkRasaAvailability();
                if (!isRasaAvailable) {
                    throw new Error('Rasa server is not available. Please ensure it is running.');
                }

                const response = await fetch('/api/rasa_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: "test email connection",
                        context: {
                            imap_settings: settings,
                            action: "test_connection"
                        }
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
                }

                const data = await response.json();

                // If there's an error in the response
                if (data.error) {
                    console.warn('Server returned error:', data.error);
                    return false;
                }

                return data.context && data.context.connected === true;
            } catch (error) {
                console.error('Error testing email connection:', error);

                // Show the error in the UI
                const event = new CustomEvent('email-connection-test', {
                    detail: {
                        success: false,
                        error: error.message || 'Connection failed'
                    }
                });
                window.dispatchEvent(event);

                return false;
            }
        }

        /**
         * Mark an email as read using MCP
         * @param {string|number} emailId - ID of the email to mark as read
         */
        async markEmailAsRead(emailId) {
            try {
                // First update local database
                await window.mailoDB.db.emails.update(emailId, { read: true });
                console.log(`Email ${emailId} marked as read locally`);

                // Then send request to MCP via Rasa if connected
                if (this.connected && window.rasaService) {
                    const response = await window.rasaService.sendMessage("mark email as read", {
                        action: "mark_email_read",
                        email_id: emailId
                    });

                    console.log('MCP mark as read response:', response);
                }
            } catch (error) {
                console.error('Error marking email as read:', error);
            }
        }

        /**
         * Delete an email using MCP
         * @param {string|number} emailId - ID of the email to delete
         */
        async deleteEmail(emailId) {
            try {
                // First delete from local database
                await window.mailoDB.db.emails.delete(emailId);
                console.log(`Email ${emailId} deleted locally`);

                // Then send delete request to MCP via Rasa if connected
                if (this.connected && window.rasaService) {
                    const response = await window.rasaService.sendMessage("delete email", {
                        action: "delete_email",
                        email_id: emailId
                    });

                    console.log('MCP delete email response:', response);
                }
            } catch (error) {
                console.error('Error deleting email:', error);
            }
        }

        /**
         * Save an email to database and notify callbacks
         * @param {Object} email - Email object to save and notify about
         * @param {boolean} notify - Whether to notify callbacks (default: true)
         */
        async saveAndNotifyEmail(email, notify = true) {
            try {
                // Generate ID if needed
                if (!email.id) {
                    email.messageId = email.messageId || `msg_${Date.now()}`;
                }

                // Make sure it has all required fields
                const completeEmail = {
                    ...email,
                    timestamp: email.timestamp || new Date().toISOString(),
                    read: email.read || false,
                    folder: email.folder || 'inbox'
                };

                // Save to database
                const id = await window.mailoDB.saveEmail(completeEmail);
                console.log(`Email saved with ID: ${id}`);

                // Update with ID and notify
                completeEmail.id = id;
                if (notify) {
                    this.notifyNewEmail(completeEmail);
                }

                return id;
            } catch (error) {
                console.error('Error saving and notifying about email:', error);
                return null;
            }
        }

        /**
         * Simulate receiving new emails (for demo purposes)
         */
        simulateNewEmails(userEmail) {
            // Probability check for simulation
            if (Math.random() < SIMULATION_PROBABILITY) {
                // Get random sender and subject
                const from = this.emailSenders[Math.floor(Math.random() * this.emailSenders.length)];
                const subject = this.emailSubjects[Math.floor(Math.random() * this.emailSubjects.length)];
                const timestamp = new Date().toISOString();

                // Create email with realistic content
                const newEmail = {
                    messageId: `msg_${Date.now()}`,
                    from: from,
                    to: userEmail || 'user@example.com',
                    subject: subject,
                    body: this.generateEmailBody(subject),
                    timestamp: timestamp,
                    read: false,
                    folder: 'inbox',
                    attachments: []
                };

                console.log('Simulated new email:', newEmail);

                // Save and notify about the new email
                this.saveAndNotifyEmail(newEmail);
            }
        }

        /**
         * Generate realistic email body based on subject (for simulation)
         */
        generateEmailBody(subject) {
            // Generate realistic email content based on subject
            const templates = {
                'Your weekly digest': `Hello there,\n\nHere's your weekly summary:\n- 5 new connections\n- 3 project updates\n- 7 unread messages\n\nHave a great week ahead!\n\nBest,\nThe Team`,

                'Important account notification': `Dear User,\n\nWe're writing to inform you about an important change to your account. Please review your security settings and ensure your contact information is up to date.\n\nThank you,\nSupport Team`,

                'Meeting invitation': `Hi,\n\nYou've been invited to a meeting on ${new Date(Date.now() + 86400000).toLocaleDateString()} at 2:00 PM.\n\nAgenda:\n1. Project updates\n2. Timeline review\n3. Next steps\n\nPlease confirm your attendance.\n\nRegards,\nProject Manager`,

                'Payment receipt': `Receipt #${Math.floor(1000 + Math.random() * 9000)}\n\nThank you for your payment of $${(Math.random() * 100).toFixed(2)}.\n\nDate: ${new Date().toLocaleDateString()}\nTransaction ID: TX-${Date.now().toString().substr(-8)}\n\nThis is an automated message. Please keep this receipt for your records.`,

                'New feature announcement': `We're excited to announce a new feature that's now available in your account! Our team has been working hard to bring you tools that make your workflow more efficient.\n\nCheck out the documentation to learn more about how to use this feature.\n\nThe Product Team`,

                'Security alert': `SECURITY NOTIFICATION\n\nWe detected a sign-in to your account from a new device. If this was you, you can ignore this message. If not, please reset your password immediately.\n\nDevice: Chrome on Windows\nLocation: New York, USA\nTime: ${new Date().toLocaleTimeString()}\n\nStay safe,\nSecurity Team`,

                'Project update': `Project Status Update\n\nProgress: 78% complete\nMilestones achieved: 4/5\nNext deadline: ${new Date(Date.now() + 604800000).toLocaleDateString()}\n\nEverything is on track. The team has completed the major development tasks and is now focusing on testing and bug fixes.\n\nProject Manager`,

                'Subscription renewal': `Your subscription will renew on ${new Date(Date.now() + 2592000000).toLocaleDateString()}.\n\nPlan: Premium\nAmount: $12.99/month\n\nIf you wish to make any changes to your subscription, please do so before the renewal date.\n\nThank you for your continued support!`
            };

            return templates[subject] || `This is a sample email regarding "${subject}". The content would typically be related to the subject matter. Thank you for using our service!`;
        }

        /**
         * Register a callback function to be called when new emails arrive
         * @param {Function} callback - Function to be called when new emails arrive
         */
        onNewEmail(callback) {
            if (typeof callback === 'function') {
                this.newEmailCallbacks.push(callback);
            }
        }

        /**
         * Notify all registered callbacks about a new email
         * @param {Object} email - The new email
         */
        notifyNewEmail(email) {
            console.log(`Notifying ${this.newEmailCallbacks.length} callbacks about new email`);
            this.newEmailCallbacks.forEach(callback => {
                try {
                    callback(email);
                } catch (error) {
                    console.error('Error in new email callback:', error);
                }
            });
        }

        /**
         * Get the current connection status
         * @returns {string} - Current connection status
         */
        getConnectionStatus() {
            return this.connectionStatus;
        }

        /**
         * Check if connected to email server
         * @returns {boolean} - True if connected
         */
        isConnected() {
            return this.connected;
        }

        /**
         * Format an email from MCP format to our application format
         * @param {Object} mcpEmail - Email in MCP format
         * @returns {Object} - Email in our application format
         */
        formatMCPEmail(mcpEmail) {
            if (this.debugMode) {
                console.log('Formatting MCP email:', mcpEmail);
            }

            // Handle different date formats
            let timestamp;
            if (mcpEmail.date) {
                // Try to parse the date
                try {
                    timestamp = new Date(mcpEmail.date).toISOString();
                } catch (e) {
                    timestamp = new Date().toISOString();
                }
            } else {
                timestamp = new Date().toISOString();
            }

            // Handle different email ID formats
            const messageId = mcpEmail.id || mcpEmail.message_id || mcpEmail.messageId || `msg_${Date.now()}`;

            // Extract "to" field from different possible locations
            let to = mcpEmail.to || '';
            if (!to && mcpEmail.recipients && Array.isArray(mcpEmail.recipients)) {
                to = mcpEmail.recipients.join(', ');
            }

            return {
                messageId: messageId,
                from: mcpEmail.from || 'unknown@example.com',
                to: to,
                subject: mcpEmail.subject || '(No subject)',
                body: mcpEmail.body || mcpEmail.content || '',
                timestamp: timestamp,
                read: !!mcpEmail.read,
                folder: mcpEmail.folder || this.currentFolder,
                attachments: mcpEmail.attachments || [],
                has_attachments: mcpEmail.has_attachments || false
            };
        }

        /**
         * Search for emails with specific criteria
         * @param {Object} criteria - Search criteria (sender, subject, date, etc.)
         * @returns {Promise<Array>} - Promise resolving to array of matching emails
         */
        async searchEmails(criteria) {
            try {
                const settings = await window.mailoDB.getImapSettings();
                if (!settings || !this.connected) {
                    console.log('Not connected or no settings. Search skipped.');
                    return [];
                }

                // Check if Rasa is available
                const isRasaAvailable = await this.checkRasaAvailability();
                if (!isRasaAvailable) {
                    throw new Error('Rasa server is not available. Please ensure it is running.');
                }

                const response = await fetch('/api/rasa_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: "search emails",
                        context: {
                            imap_settings: settings,
                            action: "search_emails",
                            search_criteria: criteria
                        }
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
                }

                const data = await response.json();

                // Handle error in response
                if (data.error) {
                    console.warn('Server returned error:', data.error);
                    return [];
                }

                // If search_results is not available, return empty array
                if (!data.context || !data.context.search_results) {
                    return [];
                }

                const formattedEmails = data.context.search_results.map(email => this.formatMCPEmail(email));

                for (const email of formattedEmails) {
                    await this.saveAndNotifyEmail(email, false);
                }

                return formattedEmails;
            } catch (error) {
                console.error('Error searching emails:', error);
                return [];
            }
        }

        /**
         * Get current unread email count
         * @returns {number} - Number of unread emails
         */
        getUnreadCount() {
            return this.unreadCount;
        }

        /**
         * Switch to a different email folder
         * @param {string} folder - Folder name to switch to
         */
        async switchFolder(folder) {
            if (!this.emailFolders.includes(folder)) {
                console.error(`Folder ${folder} does not exist`);
                return false;
            }

            this.currentFolder = folder;

            // Refresh emails for the new folder
            const settings = await window.mailoDB.getImapSettings();
            if (settings && this.connected) {
                await this.sendCheckEmailRequest(settings, { folder: folder });
                return true;
            }

            return false;
        }

        /**
         * Force a refresh of emails from the current folder
         * @returns {Promise<boolean>} - Success status
         */
        async refreshEmails() {
            try {
                console.log(`Forcing refresh of emails from ${this.currentFolder}...`);
                const settings = await window.mailoDB.getImapSettings();

                if (!settings || !this.connected) {
                    console.log('Not connected or no settings. Refresh skipped.');
                    return false;
                }

                const response = await this.sendCheckEmailRequest(settings, {
                    folder: this.currentFolder,
                    limit: 20, // Get more emails during a manual refresh
                    forceRefresh: true
                });

                return !!response;
            } catch (error) {
                console.error('Error refreshing emails:', error);
                return false;
            }
        }
    }

    // Create a singleton instance
    window.emailService = new EmailService();
    console.log('Email service initialized with MCP integration');
})();
