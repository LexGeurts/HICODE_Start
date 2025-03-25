/**
 * MailoBot Client-side JavaScript
 */
document.addEventListener('DOMContentLoaded', () => {
    // Check if required dependencies are loaded
    if (!window.mailoDB) {
        console.error('MailoDB not initialized. Please check db.js is loaded correctly.');
        alert('Application failed to initialize database. Please refresh the page or contact support.');
        return;
    }

    if (!window.emailService) {
        console.error('Email service not initialized. Please check email-service.js is loaded correctly.');
        alert('Application failed to initialize email service. Please refresh the page or contact support.');
        return;
    }

    // DOM Elements
    const chatMessages = document.querySelector('.chat-messages');
    const chatInput = document.querySelector('.chat-input textarea');
    const sendButton = document.querySelector('.send-button');
    const suggestionChips = document.querySelectorAll('.suggestion-chip');
    const clearButton = document.querySelector('.btn-clear');
    const refreshButton = document.querySelector('.btn-refresh');
    const menuItems = document.querySelectorAll('.menu-item');

    // Settings Modal Elements
    const settingsModal = document.getElementById('settingsModal');
    const closeSettingsModal = document.getElementById('closeSettingsModal');
    const imapSettingsForm = document.getElementById('imapSettingsForm');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    const testConnectionBtn = document.getElementById('testConnectionBtn');
    const statusMessage = document.getElementById('statusMessage');
    const emailProviderButtons = document.querySelectorAll('.email-provider');

    // Form fields
    const imapHost = document.getElementById('imapHost');
    const imapPort = document.getElementById('imapPort');
    const imapUsername = document.getElementById('imapUsername');
    const imapPassword = document.getElementById('imapPassword');
    const imapTLS = document.getElementById('imapTLS');

    // State
    let isTyping = false;
    let conversationContext = {};

    // Initialize
    chatInput.focus();
    scrollToBottom();
    initMailoBot();

    // Event Listeners
    chatInput.addEventListener('input', autoResizeTextarea);
    chatInput.addEventListener('keydown', handleInputKeydown);
    sendButton.addEventListener('click', sendMessage);
    suggestionChips.forEach(chip => chip.addEventListener('click', useSuggestion));
    clearButton.addEventListener('click', clearChat);
    refreshButton.addEventListener('click', refreshChat);
    menuItems.forEach(item => item.addEventListener('click', handleMenuClick));

    // Settings Modal Event Listeners
    closeSettingsModal.addEventListener('click', () => toggleSettingsModal(false));
    saveSettingsBtn.addEventListener('click', saveImapSettings);
    testConnectionBtn.addEventListener('click', testImapConnection);
    emailProviderButtons.forEach(button => {
        button.addEventListener('click', setEmailProviderDefaults);
    });

    /**
     * Initialize MailoBot and its services
     */
    async function initMailoBot() {
        try {
            console.log('Initializing MailoBot...');

            // Save the initial welcome message to the database
            const welcomeMessage = "Hello! I'm MailoBot, your email assistant. I can help you organize your inbox, draft responses, and more. How can I help you today?";
            await window.mailoDB.saveConversation({
                sender: 'bot',
                message: welcomeMessage,
                context: { type: 'welcome' }
            });

            // Load or create default IMAP settings if needed
            const settings = await window.mailoDB.getImapSettings();
            if (!settings) {
                // Create default settings for demo purposes
                await window.mailoDB.saveImapSettings({
                    host: 'imap.example.com',
                    port: 993,
                    username: 'user@example.com',
                    password: 'password',
                    tls: true
                });
                console.log('Default IMAP settings created');
            }

            // Load previous conversations for context
            await loadRecentConversations();

            // Register callback for new emails before starting the service
            window.emailService.onNewEmail(handleNewEmail);

            // Set the email service's message handler
            window.emailService.addSystemMessageToChat = addSystemMessageToChat;

            // Start the email checking service
            window.emailService.start();

            console.log('MailoBot initialization complete');
        } catch (error) {
            console.error('Error initializing MailoBot:', error);
        }
    }

    /**
     * Handle new email notifications
     */
    function handleNewEmail(email) {
        console.log('New email received:', email);

        // Create notification for new email
        showNotification(`New Email: ${email.subject}`, email.from);

        // Compose a message about the email for the user
        const emailMessage = composeEmailMessage(email);

        // Add bot message about new email
        showTypingIndicator();
        setTimeout(() => {
            const notificationTimestamp = new Date();
            hideTypingIndicator();
            addMessageToChat('bot', emailMessage, notificationTimestamp);

            // Save this conversation to the database
            window.mailoDB.saveConversation({
                sender: 'bot',
                message: emailMessage,
                context: {
                    type: 'new_email_notification',
                    emailId: email.id,
                    email: {
                        subject: email.subject,
                        from: email.from
                    }
                },
                timestamp: notificationTimestamp.toISOString() // Explicit timestamp
            });

            // Update context with the new email info
            if (!conversationContext.recentEmails) {
                conversationContext.recentEmails = [];
            }

            // Add to the front of the array (most recent first)
            conversationContext.recentEmails.unshift({
                id: email.id,
                subject: email.subject,
                from: email.from,
                timestamp: email.timestamp
            });

            // Keep only the 5 most recent emails in context
            if (conversationContext.recentEmails.length > 5) {
                conversationContext.recentEmails = conversationContext.recentEmails.slice(0, 5);
            }

        }, 1000);
    }

    /**
     * Compose a helpful message about a new email
     */
    function composeEmailMessage(email) {
        // Create a more natural and helpful message based on the email details
        const sender = email.from.includes('@') ? email.from.split('@')[0] : email.from;
        const formattedTime = new Date(email.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Customize message based on subject content
        if (email.subject.toLowerCase().includes('meeting')) {
            return `📅 You've received a meeting invitation from ${sender} at ${formattedTime}. Subject: "${email.subject}". Would you like me to check your calendar for conflicts?`;
        }
        else if (email.subject.toLowerCase().includes('payment') || email.subject.toLowerCase().includes('receipt')) {
            return `💰 A payment receipt arrived from ${sender} at ${formattedTime}. Subject: "${email.subject}". Would you like me to summarize the transaction details?`;
        }
        else if (email.subject.toLowerCase().includes('security') || email.subject.toLowerCase().includes('alert')) {
            return `⚠️ IMPORTANT: Security alert received from ${sender} at ${formattedTime}. Subject: "${email.subject}". Would you like to read this now?`;
        }
        else {
            return `📬 New email received from ${sender} at ${formattedTime}. Subject: "${email.subject}". Would you like to read it now?`;
        }
    }

    /**
     * Show browser notification
     */
    function showNotification(title, body) {
        // Check if the browser supports notifications
        if (!("Notification" in window)) {
            console.log("This browser does not support desktop notifications");
            return;
        }

        // Check if permission is already granted
        if (Notification.permission === "granted") {
            new Notification(title, { body });
        }
        // Otherwise, ask for permission
        else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    new Notification(title, { body });
                }
            });
        }
    }

    /**
     * Load recent conversations from the database
     */
    async function loadRecentConversations() {
        try {
            const conversations = await window.mailoDB.getConversations();

            // Only load the last 10 conversations if there are any
            if (conversations && conversations.length > 0) {
                const recentConversations = conversations
                    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                    .slice(0, 10);

                // Update context with historical data
                conversationContext.history = recentConversations;
                console.log('Loaded conversation history for context:', conversationContext);
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    /**
     * Auto-resize textarea as user types
     */
    function autoResizeTextarea() {
        chatInput.style.height = 'auto';
        chatInput.style.height = chatInput.scrollHeight + 'px';
    }

    /**
     * Handle keydown in the textarea (e.g., Enter to send)
     */
    function handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    /**
     * Send user message and get bot response
     */
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Current timestamp
        const timestamp = new Date();

        // Add user message to chat
        addMessageToChat('user', message, timestamp);

        // Save user message to database
        window.mailoDB.saveConversation({
            sender: 'user',
            message: message,
            context: conversationContext,
            timestamp: timestamp.toISOString() // Explicit timestamp
        });

        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Show typing indicator
        showTypingIndicator();

        // Send message to Python backend and get response
        fetch('/api/rasa_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message, context: conversationContext })
        })
            .then(response => response.json())
            .then(data => {
                const responseTimestamp = new Date();
                hideTypingIndicator();

                // Process Rasa response
                handleRasaResponse(data, responseTimestamp);
            })
            .catch(error => {
                const errorTimestamp = new Date();
                console.error('Error getting response from Rasa:', error);
                hideTypingIndicator();
                addMessageToChat('bot', 'Sorry, I encountered network error. Please try again later.', errorTimestamp);
            });
    }

    /**
     * Handle Rasa response and perform actions based on it
     * @param {Object} response - Response from Rasa backend
     * @param {Date} timestamp - Timestamp when response was received
     */
    function handleRasaResponse(response, timestamp) {
        // Process bot messages
        if (response && response.length > 0) {
            response.forEach(message => {
                if (message.text) {
                    addMessageToChat('bot', message.text, timestamp);

                    // Save bot response to database
                    window.mailoDB.saveConversation({
                        sender: 'bot',
                        message: message.text,
                        context: response.context || conversationContext,
                        timestamp: timestamp.toISOString()
                    });
                }
            });
        }

        // Process actions from Rasa
        if (response.actions && response.actions.length > 0) {
            response.actions.forEach(action => {
                executeAction(action, response.context);
            });
        }

        // Update conversation context
        if (response.context) {
            conversationContext = {
                ...conversationContext,
                ...response.context
            };
        }
    }

    /**
     * Execute actions received from Rasa
     * @param {Object} action - Action to execute
     * @param {Object} context - Context for the action
     */
    function executeAction(action, context) {
        switch (action.name) {
            case 'check_emails':
                window.emailService.checkEmails();
                break;

            case 'show_inbox':
                showInboxView();
                break;

            case 'read_email':
                if (action.emailId) {
                    getFullEmailContent(action.emailId).then(email => {
                        if (email) {
                            markEmailAsRead(action.emailId);
                            const formattedEmail = formatEmailForDisplay(email);
                            addMessageToChat('bot', formattedEmail, new Date());
                        }
                    });
                }
                break;

            case 'settings_dialog':
                showSettingsDialog();
                break;

            case 'rephrased_input':
                // Handle rephrased input from CALM
                if (context && context.original_text && context.rephrased_text) {
                    console.log(`CALM rephrased: "${context.original_text}" → "${context.rephrased_text}"`);

                    // You could show a UI indication that rephrasing occurred
                    const rephraseBadge = document.createElement('div');
                    rephraseBadge.classList.add('rephrased-badge');
                    rephraseBadge.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Rephrased`;

                    // Find the last user message and add the badge
                    const userMessages = document.querySelectorAll('.user-message');
                    if (userMessages.length > 0) {
                        const lastUserMessage = userMessages[userMessages.length - 1];
                        lastUserMessage.appendChild(rephraseBadge);
                    }

                    // Update conversation context to include the rephrasing
                    conversationContext.last_rephrased = {
                        original: context.original_text,
                        rephrased: context.rephrased_text,
                        timestamp: new Date().toISOString()
                    };
                }
                break;

            case 'show_summary':
                if (action.summary) {
                    const summaryContent = `
                    <div class="email-summary">
                        <h4>📝 Email Summary</h4>
                        <p>${action.summary}</p>
                        ${action.actionItems ?
                            `<div class="action-items">
                                <h5>Action Items:</h5>
                                <ul>${action.actionItems.map(item => `<li>${item}</li>`).join('')}</ul>
                            </div>` :
                            ''}
                    </div>`;
                    addMessageToChat('bot', summaryContent, new Date());
                }
                break;

            case 'show_translation':
                if (action.translatedText) {
                    const translationContent = `
                    <div class="email-translation">
                        <h4>🌐 Translation (${action.targetLanguage})</h4>
                        <p>${action.translatedText}</p>
                    </div>`;
                    addMessageToChat('bot', translationContent, new Date());
                }
                break;

            case 'show_analysis':
                if (action.analysis) {
                    const analysisContent = `
                    <div class="email-analysis">
                        <h4>🔍 Thread Analysis</h4>
                        <p>${action.analysis}</p>
                        <div class="thread-meta">
                            <p><strong>Participants:</strong> ${action.participants.join(', ')}</p>
                            <p><strong>Timespan:</strong> ${action.timeSpan}</p>
                        </div>
                    </div>`;
                    addMessageToChat('bot', analysisContent, new Date());
                }
                break;

            case 'show_smart_replies':
                if (action.draft) {
                    const draftContent = `
                    <div class="email-draft">
                        <h4>⚡ Generated Reply</h4>
                        <div class="draft-content">${action.draft.replace(/\n/g, '<br>')}</div>
                        
                        ${action.quickReplies ?
                            `<div class="quick-replies">
                                <h5>Quick Reply Options:</h5>
                                ${action.quickReplies.map((reply, i) =>
                                `<button class="quick-reply-btn" data-reply="${i}">${reply}</button>`
                            ).join('')}
                            </div>` :
                            ''}
                            
                        <div class="draft-actions">
                            <button class="draft-action-btn" data-action="send">Send</button>
                            <button class="draft-action-btn" data-action="edit">Edit</button>
                            <button class="draft-action-btn" data-action="discard">Discard</button>
                        </div>
                    </div>`;
                    addMessageToChat('bot', draftContent, new Date());

                    // Attach event listeners to the draft action buttons
                    document.querySelectorAll('.draft-action-btn').forEach(btn => {
                        btn.addEventListener('click', handleDraftAction);
                    });

                    // Attach event listeners to quick reply buttons
                    document.querySelectorAll('.quick-reply-btn').forEach(btn => {
                        btn.addEventListener('click', handleQuickReply);
                    });
                }
                break;
            
            // case 'handle_llm_fallback':
            //     if (action.response) {
            //         addMessageToChat('bot', action.response, new Date());
            //     }
            //     break;

            default:
                console.log('Unknown action:', action.name);
        }
    }

    /**
     * Get the full email content from the database
     * @param {number} emailId - ID of the email to retrieve
     * @returns {Promise} - Promise that resolves with the full email
     */
    async function getFullEmailContent(emailId) {
        try {
            return await window.mailoDB.db.emails.get(emailId);
        } catch (error) {
            console.error('Error fetching email content:', error);
            throw error;
        }
    }

    /**
     * Mark an email as read in the database
     * @param {number} emailId - ID of the email to mark as read
     */
    async function markEmailAsRead(emailId) {
        try {
            await window.mailoDB.db.emails.update(emailId, { read: true });
            console.log(`Email ${emailId} marked as read`);
        } catch (error) {
            console.error('Error marking email as read:', error);
        }
    }

    /**
     * Format an email for display in the chat
     * @param {Object} email - The email to format
     * @returns {string} - Formatted email HTML
     */
    function formatEmailForDisplay(email) {
        // Create a nicely formatted HTML version of the email
        const dateOptions = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        const formattedDate = new Date(email.timestamp).toLocaleDateString(undefined, dateOptions);

        return `
            <div class="email-view">
                <div class="email-header">
                    <strong>From:</strong> ${email.from}<br>
                    <strong>To:</strong> ${email.to}<br>
                    <strong>Subject:</strong> ${email.subject}<br>
                    <strong>Date:</strong> ${formattedDate}
                </div>
                <div class="email-body">
                    ${email.body.replace(/\n/g, '<br>')}
                </div>
                ${email.attachments && email.attachments.length > 0 ?
                `<div class="email-attachments">
                        <strong>Attachments:</strong> 
                        ${email.attachments.map(a => a.name).join(', ')}
                    </div>` :
                ''}
            </div>
            <div class="email-llm-actions">
                <button class="email-action-btn" data-action="summarize">📝 Summarize</button>
                <button class="email-action-btn" data-action="translate">🌐 Translate</button>
                <button class="email-action-btn" data-action="analyze">🔍 Analyze Thread</button>
                <button class="email-action-btn" data-action="smart-reply">⚡ Smart Reply</button>
            </div>
            <p class="email-actions">Would you like to reply to this email or archive it?</p>
        `;
    }

    /**
     * Format timestamp to human-readable string
     * @param {Date} timestamp - The timestamp to format
     * @returns {string} - Formatted timestamp string
     */
    function formatTimestamp(timestamp) {
        // If it's not a Date object, try to convert it
        if (!(timestamp instanceof Date)) {
            timestamp = new Date(timestamp);
        }

        // Check if timestamp is today
        const now = new Date();
        const isToday = timestamp.toDateString() === now.toDateString();

        // Format options
        const timeOptions = { hour: '2-digit', minute: '2-digit' };
        const dateTimeOptions = {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };

        // If it's today, just show the time, otherwise show date and time
        return timestamp.toLocaleString(undefined, isToday ? timeOptions : dateTimeOptions);
    }

    /**
     * Add a message to the chat
     */
    function addMessageToChat(sender, text, timestamp = new Date()) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');

        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('message-avatar');

        const avatarIcon = document.createElement('i');
        avatarIcon.classList.add('fa-solid');
        avatarIcon.classList.add(sender === 'user' ? 'fa-user' : 'fa-robot');

        avatarDiv.appendChild(avatarIcon);
        messageDiv.appendChild(avatarDiv);

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');

        const textDiv = document.createElement('div');
        textDiv.classList.add('message-text');

        // Format the text content properly
        // Check if the text contains HTML and handle accordingly
        if (/<[a-z][\s\S]*>/i.test(text)) {
            // If the text contains HTML, set it as innerHTML
            textDiv.innerHTML = text;
        } else {
            // Convert plain text to HTML with line breaks and formatting
            const formattedText = text
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/```(.*?)/gs, '<pre><code>$1</code></pre>')
                .replace(/`(.*?)`/g, '<code>$1</code>');
            textDiv.innerHTML = formattedText;
        }

        const timeDiv = document.createElement('div');
        timeDiv.classList.add('message-time');
        timeDiv.textContent = formatTimestamp(timestamp);

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        messageDiv.appendChild(contentDiv);

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    /**
     * Show typing indicator
     */
    function showTypingIndicator() {
        if (isTyping) return;

        isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-message');

        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('message-avatar');

        const avatarIcon = document.createElement('i');
        avatarIcon.classList.add('fa-solid', 'fa-robot');

        avatarDiv.appendChild(avatarIcon);
        typingDiv.appendChild(avatarDiv);

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');

        const textDiv = document.createElement('div');
        textDiv.classList.add('message-text');

        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('typing-indicator');

        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('typing-dot');
            typingIndicator.appendChild(dot);
        }

        textDiv.appendChild(typingIndicator);
        contentDiv.appendChild(textDiv);
        typingDiv.appendChild(contentDiv);

        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    function hideTypingIndicator() {
        const typingMessage = document.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
        isTyping = false;
    }

    /**
     * Use a suggestion chip
     */
    function useSuggestion(e) {
        chatInput.value = e.target.textContent;
        chatInput.focus();
        autoResizeTextarea();
    }

    /**
     * Clear chat messages with confirmation
     */
    function clearChat() {
        // Show a confirmation dialog
        const confirmClear = confirm("Are you sure you want to clear the chat history? This action cannot be undone.");

        if (confirmClear) {
            // Keep the first welcome message
            const messages = Array.from(document.querySelectorAll('.message'));
            if (messages.length > 1) {
                messages.slice(1).forEach(msg => msg.remove());
            }

            // Clear conversations from database (except welcome message)
            clearConversationsFromDB();

            // Reset conversation context
            conversationContext = {};

            // Add a confirmation message
            showTypingIndicator();
            const clearTimestamp = new Date();
            setTimeout(() => {
                hideTypingIndicator();
                addMessageToChat('bot', 'Chat history has been cleared. How else can I help you today?', clearTimestamp);
            }, 1000);
        }
    }

    /**
     * Clear conversations from the database
     */
    async function clearConversationsFromDB() {
        try {
            const conversations = await window.mailoDB.getConversations();

            // Sort by timestamp
            const sortedConversations = conversations.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

            // Keep only the first welcome message
            if (sortedConversations.length > 1) {
                const idsToDelete = sortedConversations.slice(1).map(conversation => conversation.id);

                // Delete all but the first message
                await window.mailoDB.db.conversations.bulkDelete(idsToDelete);
                console.log(`Deleted ${idsToDelete.length} conversations from database`);
            }
        } catch (error) {
            console.error('Error clearing conversations from database:', error);
        }
    }

    /**
     * Refresh chat (simulate reload)
     */
    function refreshChat() {
        const refreshButton = document.querySelector('.btn-refresh i');
        refreshButton.classList.add('fa-spin');

        // Refresh emails from the background service with userInitiated flag
        window.emailService.sendCheckEmailRequest(null, {userInitiated: true});

        setTimeout(() => {
            refreshButton.classList.remove('fa-spin');
        }, 1000);
    }

    /**
     * Handle menu item clicks
     */
    function handleMenuClick(e) {
        const menuItem = e.currentTarget;
        const menuType = menuItem.querySelector('span').textContent.toLowerCase();

        menuItems.forEach(item => item.classList.remove('active'));
        menuItem.classList.add('active');

        // Handle different menu actions
        if (menuType === 'settings') {
            showSettingsDialog();
        } else if (menuType === 'inbox') {
            showInboxView();
        } else if (menuType === 'refresh') {
            // Use userInitiated flag when manually refreshing
            window.emailService.sendCheckEmailRequest(null, {userInitiated: true});
            refreshChat();
        }
    }

    /**
     * Show settings dialog for configuring email
     */
    function showSettingsDialog() {
        // Load current settings into form
        loadCurrentSettings();

        // Show settings modal
        toggleSettingsModal(true);
    }

    /**
     * Show or hide settings modal
     * @param {boolean} show - Whether to show or hide the modal
     */
    function toggleSettingsModal(show) {
        if (show) {
            settingsModal.classList.add('active');
        } else {
            settingsModal.classList.remove('active');
        }
    }

    /**
     * Load current IMAP settings into the form
     */
    async function loadCurrentSettings() {
        try {
            const settings = await window.mailoDB.getImapSettings();

            if (settings) {
                imapHost.value = settings.host || '';
                imapPort.value = settings.port || '';
                imapUsername.value = settings.username || '';
                imapPassword.value = settings.password || '';
                imapTLS.checked = settings.tls !== false;
            }

            // Hide any previous status messages
            hideStatusMessage();

        } catch (error) {
            console.error('Error loading IMAP settings:', error);
            showStatusMessage('Error loading settings. Please try again.', false);
        }
    }

    /**
     * Save IMAP settings from the form
     */
    async function saveImapSettings(e) {
        e.preventDefault();

        if (!imapSettingsForm.checkValidity()) {
            imapSettingsForm.reportValidity();
            return;
        }

        const settings = {
            host: imapHost.value.trim(),
            port: parseInt(imapPort.value.trim(), 10),
            username: imapUsername.value.trim(),
            password: imapPassword.value,
            tls: imapTLS.checked
        };

        try {
            await window.mailoDB.saveImapSettings(settings);
            showStatusMessage('Settings saved successfully!', true);

            // Restart the email service with new settings
            window.emailService.stop();
            window.emailService.start();

        } catch (error) {
            console.error('Error saving settings:', error);
            showStatusMessage('Error saving settings. Please try again.', false);
        }
    }

    /**
     * Test IMAP connection with the current form settings
     */
    function testImapConnection(e) {
        e.preventDefault();

        if (!imapSettingsForm.checkValidity()) {
            imapSettingsForm.reportValidity();
            return;
        }

        // Show testing message
        showStatusMessage('Testing connection...', true, false);

        // For this demo, we'll simulate a successful connection after a delay
        setTimeout(() => {
            const success = Math.random() > 0.3; // 70% chance of success

            if (success) {
                showStatusMessage('Connection successful!', true);
            } else {
                showStatusMessage('Connection failed. Please check your settings.', false);
            }
        }, 1500);
    }

    /**
     * Set default settings for common email providers
     */
    function setEmailProviderDefaults(e) {
        e.preventDefault();

        const button = e.target;
        const host = button.getAttribute('data-host');
        const port = button.getAttribute('data-port');
        const tls = button.getAttribute('data-tls') === 'true';

        imapHost.value = host;
        imapPort.value = port;
        imapTLS.checked = tls;

        // If username is empty, set focus to it
        if (!imapUsername.value) {
            imapUsername.focus();
        }
    }

    /**
     * Show a status message in the settings form
     * @param {string} message - The message to show
     * @param {boolean} isSuccess - Whether it's a success message
     * @param {boolean} autoHide - Whether to automatically hide the message
     */
    function showStatusMessage(message, isSuccess, autoHide = true) {
        statusMessage.textContent = message;
        statusMessage.className = 'status-message';
        statusMessage.classList.add(isSuccess ? 'success' : 'error');
        statusMessage.style.display = 'block';

        if (autoHide) {
            setTimeout(() => {
                hideStatusMessage();
            }, 5000);
        }
    }

    /**
     * Hide the status message
     */
    function hideStatusMessage() {
        statusMessage.style.display = 'none';
    }

    /**
     * Show inbox view
     */
    function showInboxView() {
        showTypingIndicator();

        // Get emails from the database
        window.mailoDB.getEmails({ folder: 'inbox' })
            .then(emails => {
                hideTypingIndicator();

                if (emails.length === 0) {
                    addMessageToChat('bot', 'Your inbox is empty. No emails to display.');
                    return;
                }

                const unreadCount = emails.filter(email => !email.read).length;
                addMessageToChat('bot', `You have ${emails.length} emails in your inbox, ${unreadCount} unread.`);
            })
            .catch(error => {
                console.error('Error loading inbox:', error);
                hideTypingIndicator();
                addMessageToChat('bot', 'Sorry, I encountered network error loading your inbox.');
            });
    }

    /**
     * Scroll to bottom of chat messages
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Request notification permission
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
    }

    // For demo purposes, simulate a bot message after 2 seconds
    setTimeout(() => {
        showTypingIndicator();
        setTimeout(() => {
            const welcomeTimestamp = new Date();
            hideTypingIndicator();
            addMessageToChat('bot', 'How can I help with your emails today?', welcomeTimestamp);
        }, 1500);
    }, 2000);
});

// Add event listener after email display to handle LLM action buttons
document.addEventListener('click', function (e) {
    if (e.target.matches('.email-action-btn')) {
        const action = e.target.getAttribute('data-action');

        // Show typing indicator while processing
        showTypingIndicator();

        switch (action) {
            case 'summarize':
                sendToRasa('summarize this email');
                break;

            case 'translate':
                // Ask for language preference
                hideTypingIndicator();
                sendToRasa('translate this email to English');
                break;

            case 'analyze':
                sendToRasa('analyze this email thread');
                break;

            case 'smart-reply':
                sendToRasa('suggest a reply to this email');
                break;
        }
    }
});

/**
 * Handle draft action button clicks
 */
function handleDraftAction(e) {
    const action = e.target.getAttribute('data-action');

    switch (action) {
        case 'send':
            sendToRasa('send this email');
            break;

        case 'edit':
            sendToRasa('edit this draft');
            break;

        case 'discard':
            sendToRasa('discard this draft');
            break;
    }
}

/**
 * Handle quick reply button clicks
 */
function handleQuickReply(e) {
    const replyIndex = e.target.getAttribute('data-reply');
    const quickReplyText = e.target.textContent;

    // Update textarea with the quick reply
    chatInput.value = quickReplyText;
    autoResizeTextarea();

    // Focus on textarea so user can modify if needed
    chatInput.focus();
}

/**
 * Add a system message to the chat (for background processes)
 * @param {string} text - Message to add
 * @param {Date} timestamp - Timestamp for the message
 */
function addSystemMessageToChat(text, timestamp = new Date()) {
    // Only add if there's actual text content
    if (!text || text.trim() === '') return;
    
    // Add the message to chat
    showTypingIndicator();
    setTimeout(() => {
        hideTypingIndicator();
        addMessageToChat('bot', text, timestamp);
        
        // Save this conversation to the database
        window.mailoDB.saveConversation({
            sender: 'bot',
            message: text,
            context: {
                type: 'system_message',
                source: 'email_service',
                timestamp: timestamp.toISOString()
            }
        });
        
        // Update context with system message info
        conversationContext.lastSystemMessage = {
            text: text,
            timestamp: timestamp.toISOString()
        };
    }, 1000);
}

// Make the function available globally for the email service to use
window.addSystemMessageToChat = addSystemMessageToChat;