#!/bin/bash

# Function to stop background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $FLASK_PID $RASA_PID 2>/dev/null
    exit
}

# Set up trap to catch Ctrl+C
trap cleanup INT

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Rasa is installed
if ! command -v rasa &> /dev/null; then
    echo "Rasa is not installed. Please install Rasa."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Start Flask server in background
echo "Starting Flask server..."
python app.py &
FLASK_PID=$!

# Wait a moment to ensure Flask server has started
sleep 2

# Start Rasa server in background
echo "Starting Rasa server..."
rasa run --enable-api --cors "*" &
RASA_PID=$!

echo "MailoBot servers are running!"
echo "Access the application at http://localhost:3000"
echo "Press Ctrl+C to stop the servers."

# Wait for user to press Ctrl+C
wait
