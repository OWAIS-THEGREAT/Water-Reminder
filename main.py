# main.py

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from apscheduler.schedulers.background import BackgroundScheduler
from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

scheduler = BackgroundScheduler()
scheduler.start()

# Store active jobs
jobs = {}

# Email Config
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


class ReminderRequest(BaseModel):
    email: EmailStr


def send_email(receiver_email: str):
    try:
        msg = EmailMessage()

        msg["Subject"] = "💧 Drink Water Beautiful 💖"
        msg["From"] = EMAIL
        msg["To"] = receiver_email

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body{
              font-family: Arial, sans-serif;
              background: linear-gradient(135deg,#ffd6e7,#d6f3ff);
              padding:40px;
              text-align:center;
            }

            .card{
              max-width:500px;
              margin:auto;
              background:white;
              border-radius:25px;
              padding:35px;
              box-shadow:0 8px 25px rgba(0,0,0,0.12);
            }

            .emoji{
              font-size:70px;
            }

            h1{
              color:#ff4f81;
              margin-top:10px;
            }

            p{
              color:#444;
              font-size:18px;
              line-height:1.7;
            }

            .btn{
              display:inline-block;
              margin-top:20px;
              padding:14px 28px;
              border-radius:50px;
              background: linear-gradient(135deg,#4facfe,#00f2fe);
              color:white !important;
              text-decoration:none;
              font-weight:bold;
              font-size:16px;
            }

            .footer{
              margin-top:25px;
              color:#888;
              font-size:14px;
            }
          </style>
        </head>

        <body>

          <div class="card">

            <div class="emoji">💧</div>

            <h1>Hydration Reminder 💖</h1>

            <p>
              Hii Babu Jaan 🌸 <br><br>

              Time to drink some water 💧 <br>

              Stay healthy, glowing and cute always ✨
            </p>

            <a class="btn">
              Drink Water Now 🥤
            </a>

            <div class="footer">
              Sent with love every 💕
            </div>

          </div>

        </body>
        </html>
        """

        msg.set_content("Drink water 💧")

        # HTML Email
        msg.add_alternative(html_content, subtype="html")

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, PASSWORD)
            smtp.send_message(msg)

        print(f"HTML email sent to {receiver_email}")

    except Exception as e:
        print("Error sending email:", e)


@app.post("/start-reminder")
def start_reminder(data: ReminderRequest):

    if data.email in jobs:
        return {"message": "Reminder already running"}
    
    send_email(data.email)

    # # Send every hour
    # job = scheduler.add_job(
    #     send_email,
    #     "interval",
    #     minutes=1,
    #     args=[data.email],
    #     id=data.email,
    # )

    # jobs[data.email] = job

    return {
        "message": f"Hourly water reminder started for {data.email}"
    }


@app.post("/stop-reminder")
def stop_reminder(data: ReminderRequest):

    if data.email not in jobs:
        return {"message": "No active reminder found"}

    jobs[data.email].remove()
    del jobs[data.email]

    return {
        "message": f"Reminder stopped for {data.email}"
    }


@app.get("/")
def home():
    return {"message": "Water Reminder API Running 🚀"}