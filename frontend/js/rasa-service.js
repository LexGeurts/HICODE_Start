/**
 * Rasa Service for MailoBot
 * Handles communication with Rasa CALM backend
 */

// Configure the base URL for Rasa server
const RASA_BASE_URL = 'http://localhost:5005'; // Change to your Rasa server URL
const RASA_API_TIMEOUT = 10000; // 10 seconds

class RasaService {
    constructor() {
        console.log('Initializing Rasa service...');
        this.sessionId = this.generateSessionId();

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
                    'Origin': window.location.origin
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
        }
    }

    /**
     * Generate a unique session ID
     * @returns {string} - Unique session ID
     */
    generateSessionId() {
        return 'web_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Send a message to Rasa and get a response
     * @param {string} message - User message
     * @param {Object} context - Conversation context
     * @returns {Promise} - Promise that resolves with Rasa's response
     */
    async sendMessage(message, context = {}) {
        try {
            const payload = {
                sender: this.sessionId,
                message: message,
                metadata: {
                    context: context
                }
            };

            const response = await this.callRasaAPI('/webhooks/rest/webhook', 'POST', payload);
            return this.processRasaResponse(response, context);
        } catch (error) {
            console.error('Error sending message to Rasa:', error);

            // Fallback to local response generation if Rasa is unavailable
            if (window.generateBotResponse) {
                const fallbackResponse = await window.generateBotResponse(message);
                return {
                    messages: [{ type: 'text', text: fallbackResponse }],
                    context: context,
                    isFallback: true
                };
            }

            throw error;
        }
    }

    /**
     * Process the response from Rasa into a standardized format
     * @param {Array} response - Raw response from Rasa
     * @param {Object} context - Original context sent with the request
     * @returns {Object} - Processed response object with messages and actions
     */
    processRasaResponse(response, context) {
        const result = {
            messages: [],
            actions: [],
            context: { ...context }
        };

        // Process each response item from Rasa
        response.forEach(item => {
            // Handle text messages
            if (item.text) {
                result.messages.push({
                    type: 'text',
                    text: item.text
                });
            }

            // Handle images
            if (item.image) {
                result.messages.push({
                    type: 'image',
                    url: item.image
                });
            }

            // Handle custom actions
            if (item.custom) {
                if (item.custom.action) {
                    result.actions.push(item.custom.action);
                }

                // Update context from custom payload
                if (item.custom.context) {
                    result.context = {
                        ...result.context,
                        ...item.custom.context
                    };
                }
            }

            // Handle buttons
            if (item.buttons) {
                result.messages.push({
                    type: 'buttons',
                    text: item.text || '',
                    buttons: item.buttons
                });
            }
        });

        return result;
    }

    /**
     * Call Rasa API endpoints
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {Object} data - Request payload
     * @returns {Promise} - Promise that resolves with the API response
     */
    async callRasaAPI(endpoint, method = 'GET', data = null) {
        const url = `${RASA_BASE_URL}${endpoint}`;

        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: RASA_API_TIMEOUT
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), RASA_API_TIMEOUT);
            options.signal = controller.signal;

            const response = await fetch(url, options);
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }
}

// Create a singleton instance
window.rasaService = new RasaService();
console.log('Rasa service initialized successfully');
