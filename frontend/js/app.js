/**
 * MailoBot Client-side JavaScript
 */
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatMessages = document.querySelector('.chat-messages');
    const chatInput = document.querySelector('.chat-input textarea');
    const sendButton = document.querySelector('.send-button');
    const suggestionChips = document.querySelectorAll('.suggestion-chip');
    const clearButton = document.querySelector('.btn-clear');
    const refreshButton = document.querySelector('.btn-refresh');
    const menuItems = document.querySelectorAll('.menu-item');

    // State
    let isTyping = false;

    // Initialize
    chatInput.focus();
    scrollToBottom();

    // Event Listeners
    chatInput.addEventListener('input', autoResizeTextarea);
    chatInput.addEventListener('keydown', handleInputKeydown);
    sendButton.addEventListener('click', sendMessage);
    suggestionChips.forEach(chip => chip.addEventListener('click', useSuggestion));
    clearButton.addEventListener('click', clearChat);
    refreshButton.addEventListener('click', refreshChat);
    menuItems.forEach(item => item.addEventListener('click', handleMenuClick));

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

        // Add user message to chat
        addMessageToChat('user', message);

        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Show typing indicator
        showTypingIndicator();

        // Send message to backend server which forwards to Rasa
        fetch('/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message, sender: 'user' }),
        })
            .then(response => response.json())
            .then(data => {
                hideTypingIndicator();

                if (data.success && data.messages && data.messages.length > 0) {
                    // Add each bot response to the chat
                    data.messages.forEach(msg => {
                        addMessageToChat('bot', msg.text || "I'm processing your request.");
                    });
                } else {
                    // Fallback if no valid response
                    addMessageToChat('bot', "I'm having trouble understanding. Could you rephrase that?");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                hideTypingIndicator();
                addMessageToChat('bot', "Sorry, I'm unable to connect to the server at the moment.");
            });
    }

    /**
     * Add a message to the chat
     */
    function addMessageToChat(sender, text) {
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

        const textParagraph = document.createElement('p');
        textParagraph.textContent = text;

        textDiv.appendChild(textParagraph);

        const timeDiv = document.createElement('div');
        timeDiv.classList.add('message-time');
        timeDiv.textContent = 'Just now';

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
     * Clear chat messages
     */
    function clearChat() {
        // Keep the first welcome message
        const messages = Array.from(document.querySelectorAll('.message'));
        if (messages.length > 1) {
            messages.slice(1).forEach(msg => msg.remove());
        }
    }

    /**
     * Refresh chat (simulate reload)
     */
    function refreshChat() {
        const refreshButton = document.querySelector('.btn-refresh i');
        refreshButton.classList.add('fa-spin');
        setTimeout(() => {
            refreshButton.classList.remove('fa-spin');
        }, 1000);
    }

    /**
     * Handle menu item clicks
     */
    function handleMenuClick(e) {
        menuItems.forEach(item => item.classList.remove('active'));
        e.currentTarget.classList.add('active');
    }

    /**
     * Scroll to bottom of chat messages
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // For demo purposes, simulate a bot message after 2 seconds
    setTimeout(() => {
        showTypingIndicator();
        setTimeout(() => {
            hideTypingIndicator();
            addMessageToChat('bot', 'How can I help with your emails today?');
        }, 1500);
    }, 2000);
});
