import google.generativeai as genai

def generate_follow_up_1(email_content, ai_response):
    follow_up_1_prompt = f"""Based on the email content: '{email_content}' and the AI response: '{ai_response}', 
    suggest a follow-up email focused on scheduling a call. The follow-up should include a specific request for 
    scheduling a meeting to discuss further details."""
    follow_up_1_response = genai.GenerativeModel('gemini-1.5-flash').generate_content(follow_up_1_prompt)
    return follow_up_1_response.text.strip()

def generate_follow_up_2(email_content, ai_response):
    follow_up_2_prompt = f"""Based on the email content: '{email_content}' and the AI response: '{ai_response}', 
    suggest a follow-up email focused on clarifying expectations and next steps. The follow-up should request 
    any additional information needed to move forward with the discussion."""
    follow_up_2_response = genai.GenerativeModel('gemini-1.5-flash').generate_content(follow_up_2_prompt)
    return follow_up_2_response.text.strip()
