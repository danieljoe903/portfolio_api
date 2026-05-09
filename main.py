import os

import resend
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

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
MAIL_TO = os.getenv("MAIL_TO", "danieljoe903@gmail.com")

resend.api_key = RESEND_API_KEY


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str


@app.get("/")
def home():
    return {"message": "Portfolio API is running"}


@app.post("/contact")
def submit_contact(data: ContactForm):
    if not RESEND_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Resend API key is missing.",
        )

    try:
        resend.Emails.send(
            {
                "from": "Portfolio Contact <onboarding@resend.dev>",
                "to": [MAIL_TO],
                "subject": f"New portfolio contact from {data.name}",
                "reply_to": data.email,
                "html": f"""
                    <h2>New Portfolio Contact Message</h2>

                    <p><strong>Name:</strong> {data.name}</p>
                    <p><strong>Email:</strong> {data.email}</p>

                    <p><strong>Message:</strong></p>
                    <p>{data.message}</p>
                """,
            }
        )

        return {
            "success": True,
            "message": f"Thank you {data.name}, your message was sent successfully.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}",
        )