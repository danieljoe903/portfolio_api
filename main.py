import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://danieljoe903.github.io",
        "https://danieljoe903.github.io/portfolio_react",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
MAIL_TO = os.getenv("MAIL_TO", GMAIL_USER)

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

@app.get("/")
def home():
    return {"message": "Portfolio API is running"}

@app.post("/contact")
def submit_contact(data: ContactForm):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise HTTPException(status_code=500, detail="Email settings are missing.")

    msg = EmailMessage()
    msg["Subject"] = f"New portfolio contact from {data.name}"
    msg["From"] = GMAIL_USER
    msg["To"] = MAIL_TO
    msg["Reply-To"] = data.email

    msg.set_content(
        f"""
New portfolio contact message

Name: {data.name}
Email: {data.email}

Message:
{data.message}
""".strip()
    )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {
        "success": True,
        "message": f"Thank you {data.name}, your message was sent successfully."
    }