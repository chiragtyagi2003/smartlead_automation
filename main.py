import streamlit as st
import pandas as pd
import datetime
from email_classification import classify_email
from email_generation import generate_reply
from email_followups import generate_follow_up_1, generate_follow_up_2
from database import fetch_emails_from_rds
from utils import prepare_payload, feedback_and_comparison

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
    # response = send_reply_email(payload, campaign_id)
    # st.write(response)


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
