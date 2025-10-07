
## Getting Started

### Prerequisites

- Python (v3.8 or higher)
- Pip (Python package manager)

---

### Installation

1. **Install dependencies**

   ```bash
   # Install Python dependencies for Flask server
   pip install -r requirements.txt

   # Install Python dependencies for Rasa backend
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

2. **Train the Rasa model**

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