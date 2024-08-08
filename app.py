import streamlit as st
import pandas as pd
import datetime
import google.generativeai as genai
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("smartlead_creds.json")
    firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

API_KEY = os.getenv("gen_API_Key")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

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

# Function to fetch emails from Firestore
def fetch_emails_from_firestore():
    emails_ref = db.collection('emails')  # Assuming your collection is named 'emails'
    docs = emails_ref.stream()
    email_data = []
    for doc in docs:
        data = doc.to_dict()
        timestamp = data.get("time_replied")
        if timestamp:
            # Convert Firestore timestamp to Python datetime
            date = datetime.datetime.fromtimestamp(timestamp.timestamp()).strftime("%Y-%m-%d %H:%M:%S")
        else:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Default to current date if not provided
        email_data.append({
            "sender_email": data.get("to_email"),
            "email_content": data.get("reply_message_text"),
            "date": date
        })
    return email_data

# Fetch emails
email_data = fetch_emails_from_firestore()

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
def send_email(response, recipient_info):
    # Dummy sending logic
    st.write(f"Sending email to {recipient_info}: {response}")

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
    send_email(response_text, selected_email["sender_email"])

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
