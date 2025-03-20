/**
 * MailoBot Rasa Service
 * Handles communication with the Rasa backend
 */

// Configuration
const RASA_BASE_URL = 'http://localhost:5005';
const RASA_WEBHOOKS_URL = `${RASA_BASE_URL}/webhooks/rest/webhook`;
const VERBOSE_LOGGING = true;  // Set to true for detailed logs

(function () {
    class RasaService {
        constructor() {
            console.log('Initializing Rasa service...');
            this.sessionId = this.generateSessionId();
            this.streamMode = false;

            // Check CORS configuration on initialization
            this.checkCorsConfig();
        }

        /**
         * Check if CORS is correctly configured on the Rasa server
         */
        async checkCorsConfig() {
            try {
                // Simple OPTIONS preflight request check
                const response = await fetch(`${RASA_BASE_URL}/version`, {
                    method: 'OPTIONS',
                    headers: {
                        'Origin': window.location.origin,
                        'Access-Control-Request-Method': 'GET',
                        'Access-Control-Request-Headers': 'Content-Type'
                    }
                });

                if (response.ok) {
                    console.log('CORS is properly configured on Rasa server');
                } else {
                    console.warn('Rasa server might have CORS issues. Response code:', response.status);
                }
            } catch (error) {
                console.error('Failed to check Rasa CORS configuration:', error);
                console.warn('If you\'re seeing CORS errors, make sure to start Rasa with: --enable-api --cors "*"');

                // Show user-friendly error
                this.displayCorsError();
            }
        }

        /**
         * Display a user-friendly CORS error message
         */
        displayCorsError() {
            // Create a special message to display to the user
            const event = new CustomEvent('rasa-error', {
                detail: {
                    type: 'cors',
                    message: 'Cannot connect to the Rasa server due to CORS restrictions. Please make sure the server is running with proper CORS settings.'
                }
            });
            window.dispatchEvent(event);
        }

        /**
         * Generate a unique session ID
         * @returns {string} - Unique session ID
         */
        generateSessionId() {
            // Generate a random session ID with timestamp to ensure uniqueness
            const timestamp = new Date().getTime();
            const random = Math.floor(Math.random() * 10000);
            return `session_${timestamp}_${random}`;
        }

        /**
         * Send a message to Rasa and get a response
         * @param {string} message - User message
         * @param {Object} context - Conversation context
         * @returns {Promise} - Promise that resolves with Rasa's response
         */
        async sendMessage(message, context = {}) {
            try {
                if (VERBOSE_LOGGING) {
                    console.log('Sending message to Rasa:', message);
                    console.log('With context:', context);
                }

                const payload = {
                    sender: this.sessionId,
                    message: message,
                    metadata: context
                };

                // Add CORS mode explicitly
                const response = await fetch(RASA_WEBHOOKS_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Origin': window.location.origin
                    },
                    body: JSON.stringify(payload),
                    mode: 'cors',  // Explicitly set CORS mode
                    credentials: 'omit'  // Don't send credentials
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                if (VERBOSE_LOGGING) {
                    console.log('Received response from Rasa:', data);
                }

                // Process response into standard format with merged context
                return this.processResponse(data, context);
            } catch (error) {
                console.error('Error communicating with Rasa server:', error);

                // If this is a CORS error, display the specific message
                if (error.message.includes('CORS') || error.message.includes('NetworkError')) {
                    this.displayCorsError();
                }

                // Return fallback response
                return {
                    messages: [{ text: 'Sorry, I\'m having trouble connecting to my brain right now. Please check that the Rasa server is running properly.' }],
                    context: context,
                    isFallback: true
                };
            }
        }

        /**
         * Process the response from Rasa into a standardized format
         * @param {Array} response - Raw response from Rasa
         * @param {Object} context - Original context sent with the request
         * @returns {Object} - Processed response object with messages and actions
         */
        processResponse(response, originalContext = {}) {
            const result = {
                messages: [],
                context: { ...originalContext },
                actions: []
            };

            if (!response || response.length === 0) {
                result.messages.push({ text: 'I didn\'t receive a proper response. Please try again.' });
                return result;
            }

            // Process each response item
            response.forEach(item => {
                // Extract text messages
                if (item.text) {
                    result.messages.push({ text: item.text });
                }

                // Extract custom action if present
                if (item.custom) {
                    try {
                        const customData = typeof item.custom === 'string'
                            ? JSON.parse(item.custom)
                            : item.custom;

                        if (customData.action) {
                            result.actions.push(customData.action);

                            // Emit a custom event for action handlers
                            const event = new CustomEvent('rasa-custom-action', {
                                detail: {
                                    action: customData.action,
                                    context: customData.context || {}
                                }
                            });
                            window.dispatchEvent(event);
                        }

                        // Update context from custom data if available
                        if (customData.context) {
                            result.context = {
                                ...result.context,
                                ...customData.context
                            };
                        }
                    } catch (e) {
                        console.error('Error processing custom payload:', e);
                    }
                }

                // Extract images if present
                if (item.image) {
                    result.messages.push({ type: 'image', url: item.image });
                }

                // Extract buttons if present
                if (item.buttons && item.buttons.length > 0) {
                    const lastMessage = result.messages[result.messages.length - 1] || { text: '' };
                    lastMessage.buttons = item.buttons;

                    // If we just created a new message for buttons, add it
                    if (result.messages.length === 0 || result.messages[result.messages.length - 1] !== lastMessage) {
                        result.messages.push(lastMessage);
                    }
                }
            });

            return result;
        }
    }

    // Create a singleton instance
    window.rasaService = new RasaService();
    console.log('Rasa service initialized');
})();
