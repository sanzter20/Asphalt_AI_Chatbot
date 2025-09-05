# 🛠️ Asphalt_AI_Chatbot
An interactive AI-powered chatbot built with Streamlit, Google Gemini (Generative AI), PostgreSQL, and Voice Interaction.
This chatbot provides real-time insights into an asphalt plant’s operations — fetching live data from the database, generating SQL queries from natural language, and speaking responses back to the user.

🚀 Features

🤖 AI Query Conversion: Converts natural language questions into SQL queries using Google Gemini.

📊 Real-time Plant Data: Fetches current values like temperature, moisture, production efficiency, etc., from PostgreSQL.

🔊 Voice Support: Uses pyttsx3 (Text-to-Speech) and SpeechRecognition for interactive conversation.

🎨 Interactive Dashboard: Beautiful UI built with Streamlit + Plotly charts for data visualization.

⚡ Custom Styling: Animated headers, FAQ section, and styled sidebar for enhanced UX.

📂 Project Structure
asphalt_chatbot/
│── asphalt_chatbot.py   # Main Streamlit application
│── requirements.txt     # Dependencies
│── README.md            # Project documentation
│── .env                 # Environment variables (API keys, DB credentials)


🛠️ Installation
1. Clone the repo
git clone https://github.com/sanzter20/asphalt_chatbot.git
cd asphalt_chatbot

2. Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

⚙️ Configuration

Create a .env file in the project root with your credentials:

GENAI_API_KEY=your_google_genai_key

POSTGRESQL_USER=your_user
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_HOST=your_host
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=your_database

▶️ Usage

Run the Streamlit app:

streamlit run asphalt_chatbot.py


Streamlit will:

Start a local server (usually at http://localhost:8501)
Automatically opens your default web browser with that page

📊 Example Queries

“What is the current aggregate temperature?”
“Get the gas consumption of today.”
“Show me the total mix tons so far today.”
“List all mix IDs used for asphalt production.”



🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.
