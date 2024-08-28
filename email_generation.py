import google.generativeai as genai

def generate_reply(classified_details):
    generate_reply_prompt = f"""On behalf of Qubit Capital, can you generate a reply to the email received from our 
    client in a professional manner? The details are: {classified_details}, provide the reply to this email from Qubit Capital in a professional manner."""
    reply_response = genai.GenerativeModel('gemini-1.5-flash').generate_content(generate_reply_prompt)
    return reply_response.text
