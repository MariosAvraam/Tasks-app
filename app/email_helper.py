import smtplib
from email.mime.text import MIMEText
from datetime import date
from .models import Task, User, Board, Column
from . import app
from datetime import timedelta
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = getenv("SMTP_SERVER")
SMTP_PORT = getenv("SMTP_PORT")
EMAIL_ADDRESS = getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = getenv("EMAIL_PASSWORD")

def send_email(subject, body, to_email):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = to_email
            
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
        return False

def send_task_reminders():
    # Use the app's context to query the database
    with app.app_context():
        # Fetch all registered users
        users = User.query.all()

        for user in users:
            # Fetch tasks that have a deadline within the specified range
            tasks_due = (Task.query
                         .join(Column, Task.column_id == Column.id)
                         .join(Board, Column.board_id == Board.id)
                         .join(User, Board.user_id == User.id)
                         .filter(User.id == user.id, 
                                 Task.completed == False,
                                 Column.title != "Done",
                                 Task.deadline >= date.today() - timedelta(days=3),
                                 Task.deadline <= date.today() + timedelta(days=7))
                         .all())

            # Format tasks for the email
            email_body = ""
            if tasks_due:
                for task in tasks_due:
                    days_diff = (task.deadline - date.today()).days
                    if days_diff == 7:
                        msg = f"- Reminder: '{task.task}' is due in a week.\n"
                    elif days_diff == 0:
                        msg = f"- Urgent: '{task.task}' is due today.\n"
                    elif days_diff > 0:
                        msg = f"- Reminder: '{task.task}' is due in {days_diff} days.\n"
                    else:
                        msg = f"- Alert: '{task.task}' was due {abs(days_diff)} days ago.\n"
                    email_body += msg

                if email_body:
                    email_body = "Tasks notifications:\n\n" + email_body

                    # Send email to the current user and check if it was successful
                    if not send_email('Task Reminder', email_body, user.email):
                        print(f"Failed to send email to {user.email}. Skipping to next user.")
