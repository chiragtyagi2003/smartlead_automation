import pymysql
from dateutil import parser  # Import parser for string to datetime conversion
import datetime

db_host = 'rdsmain.cf4sfdz8regx.ap-south-1.rds.amazonaws.com'
db_user = 'qubit_automation'     # Replace with your RDS username
db_password = 'newpassword'    # Replace with your RDS password
db_name = 'qubit_automation_db'   # Replace with your database name

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
                    "time": row.get("datetime"),
                    "campaign_id": row.get("campaign_id")
                })

    finally:
        connection.close()
    
    return email_data
