# MailoBot

MailoBot is an AI-powered email assistant that helps monitor, organize, and manage emails. It uses Rasa Pro CALM for conversation management and OpenAI for advanced features like email drafting and RAG integration.

## About Rasa Pro CALM

MailoBot leverages Rasa Pro CALM (Conversational AI with Large Language Models) to create sophisticated conversation flows. CALM integrates the power of large language models like GPT with Rasa's robust dialogue management capabilities.

Key benefits of using CALM in MailoBot:
- Declarative flow management with JSON-based flow definitions
- Integration with OpenAI's GPT models for natural language understanding and generation
- Fallback mechanisms when predefined conversation paths are insufficient
- Slot-based context tracking across conversation flows

## Features

- Modern, responsive UI with beautiful animations
- Seamless email access via IMAP
- Conversational AI powered by Rasa Pro CALM
- Email drafting and analysis with OpenAI

## Project Structure

```
mailobot/
├── backend/                # Rasa backend
│   ├── actions/            # Custom Rasa actions
│   ├── data/               # Training data
│   └── models/             # Trained models
├── frontend/               # Web UI
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── assets/             # Static assets
├── app.py                  # Flask server
└── requirements.txt        # Python dependencies
```

## Getting Started

### Prerequisites

- Python (v3.8 or higher)
- Pip (Python package manager)

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
cd backend
rasa train
cd ..
```

### Running the Application

You can run the application in two ways:

#### Option 1: Using the convenience script

```bash
./run.sh
```

This script will:
- Start the Flask server (frontend) on port 3000
- Start the Rasa server with proper CORS settings on port 5005
- Press Ctrl+C to stop both servers

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

Open your browser and navigate to `http://localhost:3000`

## Development

- **Start an interactive Rasa shell**

```bash
cd backend
rasa shell
```

## Next Steps

- Integrate with email providers via IMAP
- Implement OpenAI for advanced email processing
- Set up authentication
- Add email categorization and priority sorting

## License

This project is licensed under the ISC License - see the LICENSE file for details.
