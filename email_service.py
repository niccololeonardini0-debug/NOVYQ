import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st


def send_notification_email(patient_name, symptoms, priority, doctor_email):
    sender_email = st.secrets.get("EMAIL_USER", "").strip()
    sender_password = st.secrets.get("EMAIL_PASSWORD", "").strip()

    if not sender_email or not sender_password:
        print("Email non inviata: EMAIL_USER o EMAIL_PASSWORD mancanti nei secrets.")
        return False

    if not doctor_email:
        print("Email non inviata: doctor_email mancante.")
        return False

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = doctor_email
    message["Subject"] = "Nuovo questionario Novyq"

    body = f"""
Nuovo questionario compilato su Novyq.

Paziente:
{patient_name}

Problema segnalato:
{symptoms}

Priorità:
{priority}

Accedi alla dashboard Novyq per visualizzare il PDF.
"""

    message.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        return True

    except Exception as e:
        print("Errore invio email:", e)
        return False