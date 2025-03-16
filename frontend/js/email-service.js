/**
 * MailoBot Email Service
 * Handles background email checking and processing
 */

// Email check interval (in milliseconds)
const EMAIL_CHECK_INTERVAL = 60000; // 1 minute

(function () {
    class EmailService {
        constructor() {
            this.isRunning = false;
            this.checkInterval = null;
            this.lastCheckTime = null;
            this.newEmailCallbacks = [];
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
            this.checkEmails();

            // Set up interval for checking emails
            this.checkInterval = setInterval(() => {
                this.checkEmails();
            }, EMAIL_CHECK_INTERVAL);
        }

        /**
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
         * Check for new emails
         */
        async checkEmails() {
            try {
                // Make sure mailoDB is available
                if (!window.mailoDB) {
                    console.error('mailoDB is not initialized. Email checking skipped.');
                    return;
                }

                const settings = await window.mailoDB.getImapSettings();
                if (!settings) {
                    console.log('No IMAP settings found. Email checking skipped.');
                    return;
                }

                console.log('Checking for new emails using settings:', settings);
                this.lastCheckTime = new Date();

                // For demonstration purposes, we'll simulate finding new emails
                // In a real implementation, this would connect to an IMAP server
                this.simulateNewEmails(settings.username);
            } catch (error) {
                console.error('Error checking emails:', error);
            }
        }

        /**
         * Simulate receiving new emails (for demo purposes)
         */
        simulateNewEmails(userEmail) {
            // Increase chance of emails (20%) to ensure testing works
            if (Math.random() < 0.2) {
                // Get random sender and subject
                const from = this.emailSenders[Math.floor(Math.random() * this.emailSenders.length)];
                const subject = this.emailSubjects[Math.floor(Math.random() * this.emailSubjects.length)];
                const timestamp = new Date().toISOString();

                // Create email with more realistic content
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

                // Save the simulated email to the database
                window.mailoDB.saveEmail(newEmail)
                    .then(id => {
                        console.log(`Simulated email saved with ID: ${id}`);

                        // Update the email with the generated ID
                        newEmail.id = id;

                        // Notify all registered callbacks about the new email
                        this.notifyNewEmail(newEmail);
                    })
                    .catch(err => {
                        console.error('Failed to save simulated email:', err);
                    });
            }
        }

        /**
         * Generate realistic email body based on subject
         */
        generateEmailBody(subject) {
            // Generate more realistic email content based on subject
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
    }

    // Create a singleton instance
    window.emailService = new EmailService();
    console.log('Email service initialized successfully');
})();
