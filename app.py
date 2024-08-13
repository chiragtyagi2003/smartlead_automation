import streamlit as st
import pandas as pd
import datetime
import google.generativeai as genai
import os
import pymysql
from dateutil import parser  # Import parser for string to datetime conversion
import requests

# Database connection details
db_host = 'rdsmain.cf4sfdz8regx.ap-south-1.rds.amazonaws.com'
db_user = 'qubit_automation'     # Replace with your RDS username
db_password = 'newpassword'    # Replace with your RDS password
db_name = 'qubit_automation_db'   # Replace with your database name

# Initialize Google Generative AI
API_KEY = os.getenv("gen_API_Key")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
SMARTLEAD_API_KEY = os.getenv("smartlead_api_key")

# Categories for email classification
Categories = [
    'Not interested in any type of service/collaboration.',
    'Out of office, please contact me with the mentioned emails.',
    'Out of office, I would like to schedule a call at a given date after returning.',
    'Would like to discuss potential partnerships/services.',
    'Would like to schedule a call.',
    'Request Information about Qubit Capital portfolio and investors the company has on board.',
    'Not raising right now but are open to discussion.',
    'Would like to schedule a call at a given time.',
    'Open to Explore, require specific service/specific geographical clients.',
    'Asked Information about specific types of service.',
    'Details/Calendars/Meet links to schedule a call.',
    'None of the above'
]
Categories_string = ', '.join(Categories)



# Function to fetch emails from AWS RDS
def fetch_emails_from_rds():
    email_data = []
    # Establish a connection to the RDS database
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # Fetch the last 10 emails, ordered by event_timestamp or another appropriate column
            sql_query = """
                SELECT to_email, reply_message_text, event_timestamp, stats_id, datetime, campaign_id
                FROM smartlead_campaign_emails
                ORDER BY event_timestamp DESC
                LIMIT 10
                """

            cursor.execute(sql_query)
            results = cursor.fetchall()

            # Process the fetched results
            for row in results:
                timestamp = row.get("event_timestamp")
                if timestamp:
                    try:
                        # Parse the string timestamp to a datetime object
                        date = parser.parse(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError):
                        # Handle invalid timestamp formats
                        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                email_data.append({
                    "sender_email": row.get("to_email"),
                    "email_content": row.get("reply_message_text"),
                    "date": date,
                    "stats_id": row.get("stats_id"),
                    # "message_id": row.get("message_id"),
                    # "email_body": row.get("email_body"),
                    "time": row.get("datetime"),
                    "campaign_id": row.get("campaign_id")  # Added this line
                })

    finally:
        connection.close()
    
    return email_data


# Fetch emails
email_data = fetch_emails_from_rds()

# Convert the list of dictionaries to a DataFrame
emails_df = pd.DataFrame(email_data)

# Define Streamlit App
st.title("Email Management and Response Generation")

# Display Emails in Sidebar
st.sidebar.header("Client Emails")
email_list = emails_df.to_dict('records')

# Create a select box for email selection
selected_email_index = st.sidebar.selectbox(
    "Select an Email", 
    range(len(email_list)), 
    format_func=lambda x: f"{email_list[x]['sender_email']} - {email_list[x]['date']}"
)


def prepare_payload(email_details, generated_reply):
    payload = {
        "email_stats_id": email_details["stats_id"],
        "email_body": generated_reply,
        # "reply_message_id": email_details["message_id"],
        # "reply_email_time": email_details["time"],
        # "reply_email_body": email_details["email_body"],
        "cc": "chiragtyagi2025@gmail.com",
        "bcc": "chirag.tyagi@qubit.capital",
        "add_signature": True,
        "to_first_name": "chirag",
        "to_last_name": "tyagi",
        "to_email": "tyagichirag2025@gmail.com" # for testing purpose
        # "to_email": email_details["sender_email"]
    }
    return payload

# Display selected email details
selected_email = email_list[selected_email_index]
st.sidebar.write(f"**Sender:** {selected_email['sender_email']}")
st.sidebar.write(f"**Date/Time:** {selected_email['date']}")
st.sidebar.write(f"**Content:** {selected_email['email_content']}")

# Initialize session state variables
if 'classified_details' not in st.session_state:
    st.session_state.classified_details = ""
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = ""
if 'follow_up_1' not in st.session_state:
    st.session_state.follow_up_1 = ""
if 'follow_up_2' not in st.session_state:
    st.session_state.follow_up_2 = ""

# Function to classify emails
def classify_email(email_content):
    classify_email_prompt = f"Can you classify the given email to one of the given categories? Email is: {email_content} Categories are: {Categories_string}"
    additional_details_prompt = " If there are some details mentioned corresponding to the category, like mentioned dates, times, emails etc, please give them also!"
    response = model.generate_content(classify_email_prompt + additional_details_prompt)
    return response.text

# Function to generate AI response
def generate_reply(classified_details):
    generate_reply_prompt = f"""On behalf of Qubit Capital, can you generate a reply to the email received from our 
    client in a professional manner? The details are: {classified_details}, provide the reply to this email from Qubit Capital in a professional manner."""
    reply_response = model.generate_content(generate_reply_prompt)
    return reply_response.text

# Function to generate Follow-Up 1
def generate_follow_up_1(email_content, ai_response):
    follow_up_1_prompt = f"""Based on the email content: '{email_content}' and the AI response: '{ai_response}', 
    suggest a follow-up email focused on scheduling a call. The follow-up should include a specific request for 
    scheduling a meeting to discuss further details."""
    follow_up_1_response = model.generate_content(follow_up_1_prompt)
    return follow_up_1_response.text.strip()

# Function to generate Follow-Up 2
def generate_follow_up_2(email_content, ai_response):
    follow_up_2_prompt = f"""Based on the email content: '{email_content}' and the AI response: '{ai_response}', 
    suggest a follow-up email focused on clarifying expectations and next steps. The follow-up should request 
    any additional information needed to move forward with the discussion."""
    follow_up_2_response = model.generate_content(follow_up_2_prompt)
    return follow_up_2_response.text.strip()

# Function to collect feedback and compare against benchmark
def feedback_and_comparison(feedback_score, benchmark_score):
    return feedback_score >= benchmark_score

# Function to send email
def send_reply_email(payload, campaign_id):
    url = f"https://server.smartlead.ai/api/v1/campaigns/{campaign_id}/reply-email-thread?api_key={SMARTLEAD_API_KEY}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # Log the response status and headers
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                # Log the entire response for debugging
                print("Error: Response is not in JSON format.")
                print("Response Content:")
                print(response.text)
                return None
        else:
            # Log the entire response for non-200 status codes
            print(f"Error: {response.status_code}")
            print("Response Content:")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Display selected email details in the main area
st.subheader("Selected Email Details")
st.write(f"**Sender:** {selected_email['sender_email']}")
st.write(f"**Date/Time:** {selected_email['date']}")
st.write(f"**Content:** {selected_email['email_content']}")

# Classify and Generate Response
if st.button("Classify and Generate Response"):
    st.session_state.classified_details = classify_email(selected_email["email_content"])
    st.session_state.ai_response = generate_reply(st.session_state.classified_details)
    
    # Generate follow-up emails
    st.session_state.follow_up_1 = generate_follow_up_1(selected_email["email_content"], st.session_state.ai_response)
    st.session_state.follow_up_2 = generate_follow_up_2(selected_email["email_content"], st.session_state.ai_response)

# Display AI response and allow editing
response_text = st.text_area("AI Generated Response:", value=st.session_state.ai_response, height=200, key="ai_response_text_area")

# Collect Feedback
feedback_score = st.slider("Rate the AI response", 1, 5, 3, key="feedback_score")
benchmark_score = 4  # Example benchmark score
if feedback_and_comparison(feedback_score, benchmark_score):
    st.success("Response meets the benchmark score.")
else:
    st.error("Response does not meet the benchmark score. Consider editing or regenerating the response.")

if st.button("Send Response", key="send_response"):
    payload = prepare_payload(selected_email, response_text)
    campaign_id = selected_email["campaign_id"]
    response = send_reply_email(payload, campaign_id)
    st.write(response)


# Display follow-up emails
st.subheader("Follow-Up Emails")
follow_up_1_content = st.text_area("Follow-Up 1 Content", value=st.session_state.follow_up_1, height=150, key="followup_1_content")
follow_up_1_date = st.date_input("Select Follow-Up Date for Follow-Up 1", datetime.date.today(), key="followup_1_date")
follow_up_1_time = st.time_input("Select Follow-Up Time for Follow-Up 1", datetime.datetime.now().time(), key="followup_1_time")
if st.button("Schedule Follow-Up 1", key="schedule_followup_1"):
    st.write(f"Follow-Up 1 scheduled for {follow_up_1_date} at {follow_up_1_time}.")

follow_up_2_content = st.text_area("Follow-Up 2 Content", value=st.session_state.follow_up_2, height=150, key="followup_2_content")
follow_up_2_date = st.date_input("Select Follow-Up Date for Follow-Up 2", datetime.date.today(), key="followup_2_date")
follow_up_2_time = st.time_input("Select Follow-Up Time for Follow-Up 2", datetime.datetime.now().time(), key="followup_2_time")
if st.button("Schedule Follow-Up 2", key="schedule_followup_2"):
    st.write(f"Follow-Up 2 scheduled for {follow_up_2_date} at {follow_up_2_time}.")
