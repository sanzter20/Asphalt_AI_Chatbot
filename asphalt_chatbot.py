import os
import google.generativeai as genai
import psycopg2
import pyttsx3
import streamlit as st
from dotenv import load_dotenv
import ctypes
import pandas as pd
import numpy as np
import plotly.express as px
import speech_recognition as sr

# Load all the environment variables
load_dotenv()

# Configure GenAI Key
genai.configure(api_key=os.getenv('GENAI_API_KEY'))


# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text


# Function to convert text to speech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


# Environment variables or fallback to default
USER = os.environ.get('POSTGRESQL_USER', 'ayush')
PASSWORD = os.environ.get('POSTGRESQL_PASSWORD', 'hs@H5d8N>hfK')
HOST = os.environ.get('POSTGRESQL_HOST', 'lns-dev-demo-2.cb82mwiiosoj.ap-south-1.rds.amazonaws.com')
PORT = os.environ.get('POSTGRESQL_PORT', 5432)
DATABASE = os.environ.get('POSTGRESQL_DATABASE', 'lnsdemo')
SCHEMA = 'asphalt'


# Function to retrieve query from the PostgreSQL database
def read_sql_query(sql):
    try:
        # Database connection parameters
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE
        )
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except (Exception, psycopg2.Error) as error:
        st.error(f"Error retrieving data: {error}")
        return []
    finally:
        if connection:
            cursor.close()
            connection.close()


# Define your prompt
prompt = [
    f"""
    You are an expert in converting English questions to PostgreSQL queries! 
    The PostgreSQL database has the schema '{SCHEMA}'. The purpose of the DB - plant_data and table 'plant_data' is to fetch the latest values of various parameters listed in its columns. It has the following columns - plant_data_id, record_time, plant_id, plant_type, job_number, mix_id, target_tph, act_pom_tph, agg_wb_tph, rec_wb_tph, ac_tph, mf_tph, asa_tph, mix_temp, tons_run, mix_tons_run, agg_temp, bh_inlet_stk_temp, ac_temp, drum_shell_temp, bh_exhaust_temp, fuel2_oil_temp, gas_meter_r1, gas_meter_r2, bt_tank_temp, bt_tank_press, ambient_temp, agg_moisture, airflow_rate, gasflow_rate, relative_humidity.

    The PostgreSQL DB code should not have ``` in the beginning or end and 'PostgreSQL DB' word in the output.

    Example 1 - What is the current aggregate temperature? The PostgreSQL DB command will be something like this: SELECT 'The current aggregate temperature is ' || ROUND(agg_temp::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data ORDER BY record_time DESC LIMIT 1;

    Example 2 - What is the current drumshell temperature? The PostgreSQL DB command will be something like this: SELECT 'The current drumshell temperature is ' || ROUND(drum_shell_temp::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data ORDER BY record_time DESC LIMIT 1;

    Example 3 - What is the current moisture percentage? The PostgreSQL DB command will be something like this: SELECT 'The current moisture percentage is ' || ROUND(agg_moisture::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data ORDER BY record_time DESC LIMIT 1;

    Example 4 - What is the production efficiency today? The PostgreSQL DB command will be something like this: SELECT 'The production efficiency today is ' || ROUND((act_pom_tph / target_tph) * 100, 2) || '%.' AS output_message FROM {SCHEMA}.plant_data WHERE record_time::date = CURRENT_DATE ORDER BY record_time DESC LIMIT 1;

    Example 5 - What is the total mix of tons so far today? The PostgreSQL DB command will be something like this: SELECT 'The total mix of tons so far today is ' || ROUND(SUM(mix_tons_run)::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data WHERE record_time::date = CURRENT_DATE;

    Example 6 - List of mix IDs used for asphalt production. The PostgreSQL DB command will be something like this: SELECT DISTINCT mix_id FROM {SCHEMA}.plant_data ORDER BY mix_id;

    Example 7 - What is the current BH exhaust temperature? The PostgreSQL DB command will be something like this: SELECT 'The current BH exhaust temperature is ' || ROUND(bh_exhaust_temp::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data ORDER BY record_time DESC LIMIT 1;

    Example 8 - What is the current AC temperature? The PostgreSQL DB command will be something like this: SELECT 'The current AC temperature is ' || ROUND(ac_temp::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data ORDER BY record_time DESC LIMIT 1;

    Example 9 - What is the current mix temperature? The PostgreSQL DB command will be something like this: SELECT 'The current mix temperature is ' || ROUND(mix_temp::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data ORDER BY record_time DESC LIMIT 1;

    Example 10 - Get the gas consumption of today. The PostgreSQL DB command will be something like this: SELECT 'The gas consumption today is ' || ROUND((COALESCE(gas_meter_r1, 0) + COALESCE(gas_meter_r2, 0))::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data WHERE record_time::date = CURRENT_DATE ORDER BY record_time DESC LIMIT 1;

    Example 11 - What is the current throughput of the plant? The PostgreSQL DB command will be something like this: SELECT 'The current throughput of the plant is ' || ROUND(act_pom_tph::numeric, 2) || '.' AS output_message FROM {SCHEMA}.plant_data ORDER BY record_time DESC LIMIT 1;

    Example 12 - Get mix tons per mix ID basis. The PostgreSQL DB command will be something like this: SELECT mix_id, ROUND(SUM(mix_tons_run)::numeric, 2) AS total_mixed_tons FROM {SCHEMA}.plant_data GROUP BY mix_id ORDER BY mix_id;

    Example 13 - What is the trend of the previous 5 periods of aggregate temperature? The PostgreSQL DB command will be something like this: SELECT record_time, agg_temp FROM {SCHEMA}.plant_data ORDER BY record_time DESC LIMIT 5;
    """
]

# Streamlit App
st.set_page_config(page_title="Empowering Industry Insights: Asphalt AI Chatbot")

# CSS for background and styles
st.markdown('''
<style>
body {  
   background-image: url('https://t3.ftcdn.net/jpg/08/04/38/96/360_F_804389694_DQzaulmKWL7fYz6tp1Vs2bLZSpMVO82p.jpg');  
   background-size: cover;
}
.custom-header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px; /* Adjust padding */
    background: rgba(67, 160, 71, 0.3); /* Light green background */
    border-radius: 20px; /* Rounded corners */
    backdrop-filter: blur(15px); /* Blur effect */
    -webkit-backdrop-filter: blur(15px); /* Safari blur effect */
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2); /* Shadow effect */
    border: 1px solid rgba(67, 160, 71, 0.5); /* Green border */
    margin-bottom: 20px; /* Bottom margin */
    animation: fallIn 2s ease-in-out; /* Animation */
}

@keyframes fallIn {
    0% {
        transform: translateY(-100%); /* Start position */
        opacity: 0; /* Start opacity */
    }
    100% {
        transform: translateY(0); /* End position */
        opacity: 1; /* End opacity */
    }
}

.custom-header-text {
    font-size: 32px; /* Font size */
    font-weight: bold; /* Font weight */
    color: #FFFFFF; /* Text color */
}

.header-logo {
    width: 100px; /* Logo width */
    height: auto; /* Maintain aspect ratio */
    margin-right: 15px; /* Spacing between logo and text */
}

.sidebar-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 20px;
}

.logo {
    width: 90%; /* Logo width */
    height: auto; /* Maintain aspect ratio */
    margin-bottom: 20px; /* Spacing */
}

.pulsing-text {
    animation: pulse-animation 2s infinite; /* Animation */
    color: #009688; /* Text color */
}

.sidebar-title {
    font-size: 25px; /* Font size */
    font-weight: bold; /* Font weight */
    color: #004D40; /* Dark green */
    margin-bottom: 10px; /* Spacing */
}

.sidebar-text {
    margin-top: 20px; /* Top margin */
    font-size: 15px; /* Font size */
    color: #FFFFFF; /* Text color */
    background-color: #00796B; /* Teal background color */
    padding: 15px 15px; /* Padding */
    border-radius: 15px; /* Rounded corners */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Shadow effect */
    text-align: left; /* Text alignment */
    font-family: emoji; /* Font family */
    transition: background-color 0.3s ease; /* Background color transition */
}

.sidebar-text:hover {
    background-color: #004D40; /* Darker green on hover */
}

.faq-section {
    background: rgba(0, 0, 0, 0.6); /* Semi-transparent dark background */
    border-radius: 15px; /* Rounded corners */
    padding: 20px; /* Padding */
    margin: 20px 0; /* Margin */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); /* Shadow effect */
}

.faq-title {
    font-size: 24px;
    font-weight: bold;
    color: #4CAF50; /* Title color */
    margin-bottom: 15px;
}

.faq-item {
    margin-bottom: 10px;
}

.faq-question {
    font-weight: bold;
    color: #00B050; /* Question color */
}

.faq-answer {
    margin-top: 5px;
    color: #FFFFFF; /* Answer color */
}
</style>

''',unsafe_allow_html=True)


def welcome_message():
    speak(
        "Hello! I'm the AI & ML Expert Optimizer. Welcome to Empowering Industry Insights: Asphalt AI Chatbot. How can I help you today?")


# Display the header with a logo and styled text using st.markdown for custom styling
st.markdown('''
<div class="custom-header-container">
    <img src="https://ochatbot.com/wp-content/uploads/2018/03/chatbot-icon.png" alt="Logo" class="header-logo">
    <h1 class="custom-header-text">Empowering Industry Insights: Asphalt AI Chatbot</h1>
</div>
''', unsafe_allow_html=True)

# Animated falling box
st.markdown('<div class="falling-box"></div>', unsafe_allow_html=True)

# Updated CSS styles
css = '''
<style>
/* Sidebar content container */
.sidebar-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 20px;
}

/* Logo styling */
.logo {
    width: 90%; /* Adjust width as needed */
    height: auto; /* Maintain aspect ratio */
    margin-bottom: 20px;
}

/* Running text animation */
@keyframes pulse-animation {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.pulsing-text {
    animation: pulse-animation 2s infinite;
    color: #fff; /* Text color */
}

/* Sidebar title styling */
.sidebar-title {
    font-size: 25px;
    font-weight: bold;
    color: #00B050; /* Title color */
    margin-bottom: 10px;
}

/* Updated Sidebar text styling */
.sidebar-text {
    margin-top: 20px;
    font-size: 15px;
    color: #fff; /* Text color */
    background-color: #4CAF50; /* Updated background color */
    padding: 15px 15px; /* Padding */
    border-radius: 15px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Shadow effect */
    text-align: left; /* Center-align text */
    font-family: emoji;
    transition: background-color 0.3s ease; /* Smooth color transition */
}

.sidebar-text:hover {
    background-color: #00796B; /* Darker background on hover */
}
</style>
'''

# Display CSS in Streamlit
st.markdown(css, unsafe_allow_html=True)

# Sidebar content
st.sidebar.markdown('''
<div class="sidebar-content">
<img src="https://images.yourstory.com/cs/images/companies/a24c8f4294fb-LivNSenseLogo-1616753765605.jpeg" alt="Livnsense logo" class="logo" style="height: 150px; width: 150px;">
    <div class="pulsing-text sidebar-title">LivNSense GreenOps AI Assistance</div>
    <div class="sidebar-text">I'm your AI chatbot, delivering cutting-edge insights into the Asphalt Plant. Get the latest real-time updates, predictions, current set points and recommended values at your fingertips. Explore more features? Just ask—I'm here to help!</div>
</div>
''', unsafe_allow_html=True)

# FAQ Section
st.sidebar.markdown('''
<div class="faq-section">
    <div class="faq-title">Frequently Asked Questions (FAQ)</div>
    <div class="faq-item">
        <div class="faq-question">Q1: How do I use this chatbot?</div>
        <div class="faq-answer">A1: Simply type your question into the input box, or speak into the mic, and the chatbot will answer it for you!</div>
    </div>
    <div class="faq-item">
        <div class="faq-question">Q2: What kind of questions can I ask?</div>
        <div class="faq-answer">A2: You can ask about various parameters related to asphalt production, such as temperatures, moisture levels, and production efficiency. Just frame your question clearly.</div>
    </div>
    <div class="faq-item">
        <div class="faq-question">Q3: How often is the data updated?</div>
        <div class="faq-answer">A3: The data is fetched in real-time from the PostgreSQL database, so you will get the most current information available.</div>
    </div>
    <div class="faq-item">
        <div class="faq-question">Q4: Can I get historical data?</div>
        <div class="faq-answer">A4: Yes, based on your input, it can provide the data.</div>
        
        
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown(css, unsafe_allow_html=True)

# Initialize state variables
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'welcome_played' not in st.session_state:
    st.session_state.welcome_played = False


# Call the welcome message function after the landing page animation if not already played
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def welcome_message():
    speak("Hello! I'm the AI & ML Expert Optimizer. Welcome to Empowering Industry Insights: Asphalt AI Chatbot. How "
          "can I help you today?")


# Ensure `welcome_message()` is called after proper setup
if not st.session_state.welcome_played:
    welcome_message()
    st.session_state.welcome_played = True

# Input box for new question
question = st.text_input(
    "'Welcome to the Asphat AI Chatbot'! Here, you can access real-time insights and assistance about Asphalt data.",
    key="input")

# Add the question to the list when submit is clicked
submit = st.button("Ask the question")
if submit and question.strip() != "":
    st.session_state.questions.append(question.strip())

# Process questions sequentially

for idx, question in enumerate(reversed(st.session_state.questions)):
    response = get_gemini_response(question, prompt)
    st.markdown(f"<div style='font-size: 16px;'>Question: {question}</div>", unsafe_allow_html=True)
    for row in read_sql_query(response):
        text_to_speak = row[0]  # Assuming row[0] contains the text to speak
        st.markdown(f"<div style='font-size: 16px ;color : red;'>{text_to_speak}</div>",
                    unsafe_allow_html=True)  # Display response in bold and consistent size



# Create a sample dataframe
data = {'created_on','agg_temp'}
df = pd.DataFrame(data)

# Create a line chart using Plotly Express
fig = px.line(df, x='created_on', y='agg_temp', title='Trend of Aggregate Temperature')

# Customize the chart
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Aggregate Temperature',
    hovermode='x',
    hovertext='Aggregate Temperature on {created_on}: {agg_temp}',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    title=dict(text='Trend of Aggregate Temperature', font=dict(size=20, color='black')),
    font=dict(family='Arial', size=14, color='black'),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

fig.update_traces(
    line=dict(color='blue', width=2, dash='dash')
)

# Add annotations
fig.update_layout(
    annotations=[
        dict(x='2022-01-01', y=20, text='Peak Temperature', showarrow=True, arrowhead=7)
    ]
)

# Add a range slider
fig.update_layout(
    xaxis=dict(
        rangeslider=dict(visible=True)
    )
)

# Display the line chart using Streamlit
st.plotly_chart(fig, use_container_width=True)


def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Speech recognition service is down."

if st.button('Speak'):
    voice_input = recognize_speech()
    st.write(f"Output: {voice_input}")



# Simulate plant data
data = pd.DataFrame({
    'Time': pd.date_range(start='1/1/2024', periods=100, freq='H'),
    'Production': np.random.randint(50, 100, 100)
})

st.line_chart(data.set_index('Time'))

