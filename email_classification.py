import google.generativeai as genai
import os

API_KEY = os.getenv("gen_API_Key")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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

def classify_email(email_content):
    classify_email_prompt = f"Can you classify the given email to one of the given categories? Email is: {email_content} Categories are: {Categories_string}"
    additional_details_prompt = " If there are some details mentioned corresponding to the category, like mentioned dates, times, emails etc, please give them also!"
    response = model.generate_content(classify_email_prompt + additional_details_prompt)
    return response.text
