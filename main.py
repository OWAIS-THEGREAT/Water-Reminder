# main.py

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from apscheduler.schedulers.background import BackgroundScheduler
from email.message import EmailMessage
import smtplib
import os
import requests
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

SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587

SMTP_LOGIN = os.getenv("BREVO_LOGIN")
SMTP_PASSWORD = os.getenv("BREVO_PASSWORD")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")


class ReminderRequest(BaseModel):
    email: EmailStr


def send_email(receiver_email: str):

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    html_content = """
    <div style="
        font-family: Arial;
        padding:40px;
        text-align:center;
        background: linear-gradient(135deg,#ffd6e7,#d6f3ff);
    ">

        <div style="
            max-width:500px;
            margin:auto;
            background:white;
            padding:35px;
            border-radius:25px;
            box-shadow:0 8px 20px rgba(0,0,0,0.1);
        ">

            <div style="font-size:70px;">💧</div>

            <h1 style="color:#ff4f81;">
                Hydration Reminder 💖
            </h1>

            <p style="
                font-size:18px;
                color:#444;
                line-height:1.8;
            ">
                Hii Babu Jaan 🌸 <br><br>

                Time to drink some water 💧 <br>

                Stay healthy, glowing and cute always ✨
            </p>

            <div style="
                margin-top:25px;
                color:#888;
                font-size:14px;
            ">
                Sent with love 💕</br>
                Yours and only yours,</br>
                Owiii
            </div>

        </div>

    </div>
    """

    payload = {
        "sender": {
            "name": "Owais 💖",
            "email": "mohammedowais6361@gmail.com"
        },
        "to": [
            {
                "email": receiver_email
            }
        ],
        "subject": "💧 Drink Water Beautiful",
        "htmlContent": html_content
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=10
    )

    print(response.status_code)
    print(response.text)


@app.post("/start-reminder")
def start_reminder(data: ReminderRequest):

    if data.email in jobs:
        return {"message": "Reminder already running"}
    
    send_email(data.email)

    # # Send every hour
    job = scheduler.add_job(
        send_email,
        "interval",
        hours=1,
        args=[data.email],
        id=data.email,
    )

    jobs[data.email] = job

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