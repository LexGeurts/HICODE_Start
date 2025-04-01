# MailoBot

MailoBot is an AI-powered email assistant designed to help users monitor, organize, and manage their emails efficiently. It leverages Rasa CALM for conversational AI and OpenAI for advanced email drafting and processing.

---

## Features

- **Email Management**: Access and manage emails via IMAP, including reading, searching, and marking emails as read.
- **Email Drafting**: Generate professional email drafts using OpenAI's GPT models.
- **Custom Actions**: Perform advanced email-related tasks like saving drafts and sending emails.
- **Interactive UI**: A modern, responsive web interface for seamless interaction.
- **Speech Recognition**: Use voice commands to interact with MailoBot.
- **Database Integration**: Save and retrieve conversations and email settings using Dexie.js.

---

## Project Structure

```
mailobot/
├── actions/                # Custom Rasa actions for email management
├── config/                 # Configuration files (e.g., OpenAI settings)
├── data/                   # Rasa training data and conversation flows
├── frontend/               # Web-based user interface
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── index.html          # Main HTML file
├── prompts/                # Jinja2 templates for OpenAI prompts
├── utils/                  # Utility modules (e.g., email handling, OpenAI integration)
├── app.py                  # Flask server for backend API
└── requirements.txt        # Python dependencies
```

---

## Getting Started

### Prerequisites

- Python (v3.8 or higher)
- Pip (Python package manager)

---

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd mailobot
   ```

2. **Install dependencies**

   ```bash
   # Install Python dependencies for Flask server
   pip install -r requirements.txt

   # Install Python dependencies for Rasa backend
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Train the Rasa model**

   ```bash
   rasa train
   cd ..
   ```

---

### Running the Application

You can run the application in two ways:

#### Option 1: Using the convenience script

```bash
./run.sh
```

This script will:

- Start the Rasa server with proper CORS settings on port 5005
- Start the Flask server (frontend) on port 5000
- Press `Ctrl+C` to stop both servers

#### Option 2: Starting servers manually

1. **Start the Flask server**

   ```bash
   python app.py
   ```

2. **Start the Rasa server (in a separate terminal)**

   ```bash
   rasa run --enable-api --cors "*"
   ```

   > **IMPORTANT**: The `--cors "*"` parameter is essential for the frontend to communicate with the Rasa API. Without it, you'll encounter CORS errors in your browser.

3. **Access the application**

   Open your browser and navigate to `http://localhost:5000`

---

## Usage

### Key Functionalities

1. **Email Management**
   - Check unread emails in your inbox.
   - Search for emails by sender, subject, or keywords.

2. **Email Drafting**
   - Generate email drafts with tone using OpenAI.
   - Save drafts to your email provider's drafts folder.

3. **Email Sending**
   - Send emails directly from the application.

4. **Conversation History**
   - View and manage past conversations with MailoBot - Coming soon.

5. **Settings**
   - Configure IMAP settings for your email account.

---

### Configuration

#### OpenAI Integration

MailoBot uses OpenAI's GPT models for email drafting and processing. To enable this feature:

1. Set up your OpenAI API key as an environment variable:

   ```bash
   export OPENAI_API_KEY=<your-api-key>
   ```

2. (Optional) Configure additional OpenAI settings in `config/openai.yml`.

#### IMAP Settings

IMAP settings can be configured via the settings modal in the frontend or by editing the `settings/imap_settings.json` file.

---

## Development

### Frontend

The frontend is built using HTML, CSS, and JavaScript. Key files include:

- `frontend/index.html`: Main HTML file.
- `frontend/js/`: JavaScript files for client-side logic.
- `frontend/css/`: Stylesheets for the UI.

### Backend

The backend consists of:

- **Flask Server**: Handles API requests and serves the frontend.
- **Rasa CALM**: Manages conversational AI and custom actions.

---

## Next Steps

- **Email Categorization**: Automatically categorize emails based on content.
- **Priority Sorting**: Highlight important emails.
- **Authentication**: Add user authentication for secure access.
- **Enhanced Voice Commands**: Expand speech recognition capabilities.
