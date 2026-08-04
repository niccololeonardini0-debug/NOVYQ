import sqlite3
import os
import streamlit as st
import psycopg2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # =========================
    # USERS (LOGIN STUDI)
    # =========================
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        studio_id TEXT UNIQUE NOT NULL,
        doctor_name TEXT NOT NULL,
        doctor_email TEXT NOT NULL
    )
    """)

    # =========================
    # REQUESTS (PAZIENTI)
    # =========================
    c.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        patient_surname TEXT,
        patient_age INTEGER,
        birth_date TEXT,
        tax_code TEXT,
        birth_place TEXT,
        address TEXT,
        phone TEXT,
        email TEXT,
        symptoms TEXT,
        anamnesis TEXT,
        ai_report TEXT,
        stato TEXT,
        created_at TEXT,
        studio_id TEXT,
        pdf_path TEXT,
        risposta_medico TEXT,
        consenso_privacy INTEGER,
        data_consenso TEXT,
        visitato INTEGER DEFAULT 0,
        data_visita TEXT,
        firma_paziente TEXT,
        doctor_note TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS clinical_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        request_id INTEGER,
        sintesi TEXT,
        diagnosi TEXT,
        red_flags TEXT,
        priorita TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("ALTER TABLE requests ADD COLUMN IF NOT EXISTS visitato INTEGER DEFAULT 0")
    c.execute("ALTER TABLE requests ADD COLUMN IF NOT EXISTS data_visita TEXT")
    c.execute("ALTER TABLE requests ADD COLUMN IF NOT EXISTS firma_paziente TEXT")
    c.execute("ALTER TABLE requests ADD COLUMN IF NOT EXISTS doctor_note TEXT")

    conn.commit()
    conn.close()



def login(username, password):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT
        id,
        username,
        studio_id,
        doctor_name
    FROM users
    WHERE username=%s AND password=%s
    """, (username, password))

    row = c.fetchone()
    conn.close()
    return row

def get_conn():

    return psycopg2.connect(
        st.secrets["DATABASE_URL"]
    )


import sqlite3
import json
from datetime import datetime

def insert_request(
    patient_data,
    studio_id,
    answers,
    ai_report=None,
    stato="nuovo",
    pdf_path=None,
    consenso_privacy=False,
    data_consenso=None
):

    conn = get_conn()
    c = conn.cursor()

    nome = patient_data.get("nome", "")
    cognome = patient_data.get("cognome", "")
    eta = patient_data.get("eta", "")
    data_nascita = patient_data.get("data_nascita", "")
    codice_fiscale = patient_data.get("codice_fiscale", "")
    luogo_nascita = patient_data.get("luogo_nascita", "")
    residenza = patient_data.get("residenza", "")
    telefono = patient_data.get("telefono", "")
    email = patient_data.get("email", "")

    if ai_report is None:
        ai_report = {}

    if isinstance(answers, dict):
        answers_json = json.dumps(answers, ensure_ascii=False)
    else:
        answers_json = str(answers)

    if isinstance(ai_report, dict):
        ai_report_json = json.dumps(ai_report, ensure_ascii=False)
    else:
        ai_report_json = str(ai_report)

    symptoms = ""

    if isinstance(answers, dict):

        root = answers.get("root", {})

        if isinstance(root, dict):

            symptoms = root.get("answer", "")

            if isinstance(symptoms, list):
                symptoms = ", ".join(symptoms)

        else:
            symptoms = str(root)

    c.execute("""
    INSERT INTO requests (
        patient_name,
        patient_surname,
        patient_age,
        birth_date,
        tax_code,
        birth_place,
        address,
        phone,
        email,
        symptoms,
        anamnesis,
        ai_report,
        stato,
        created_at,
        studio_id,
        pdf_path,
        consenso_privacy,
        data_consenso
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """, (
        nome,
        cognome,
        eta,
        data_nascita,
        codice_fiscale,
        luogo_nascita,
        residenza,
        telefono,
        email,
        symptoms,
        answers_json,
        ai_report_json,
        stato,
        datetime.now().isoformat(),
        studio_id,
        pdf_path,
        1 if consenso_privacy else 0,
        data_consenso
    ))
    request_id = c.fetchone()[0]

    conn.commit()
    conn.close()

    return request_id

def save_signature(request_id, firma):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE requests
    SET firma_paziente=%s
    WHERE id=%s
    """, (
        firma,
        request_id
    ))

    conn.commit()
    conn.close()

def save_doctor_note(request_id, note):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE requests
    SET doctor_note=%s
    WHERE id=%s
    """, (
        note,
        request_id
    ))

    conn.commit()
    conn.close()


def get_requests(studio_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT
    id,
    patient_name,
    patient_surname,
    patient_age,
    symptoms,
    anamnesis,
    ai_report,
    created_at,
    pdf_path,
    visitato,
    doctor_note
    FROM requests
    WHERE studio_id=%s
    ORDER BY visitato ASC, created_at DESC
    """, (studio_id,))

    data = c.fetchall()

    conn.close()

    return data


def update_status(request_id, stato):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE requests
    SET stato=%s
    WHERE id=%s
    """, (stato, request_id))

    conn.commit()
    conn.close()


def add_medical_response(request_id, risposta):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE requests
    SET risposta_medico=%s
    WHERE id=%s
    """, (risposta, request_id))

    conn.commit()
    conn.close()

def get_patients(studio_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT
        id,
        patient_name,
        patient_surname,
        patient_age,
        symptoms,
        anamnesis,
        ai_report,
        created_at,
        pdf_path
    FROM requests
    WHERE studio_id=%s
    ORDER BY id DESC
    """, (studio_id,))

    data = c.fetchall()

    conn.close()

    return data


def save_history(patient_id, request_id, sintesi, diagnosi, red_flags, priorita):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO clinical_history (
        patient_id,
        request_id,
        sintesi,
        diagnosi,
        red_flags,
        priorita
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        patient_id,
        request_id,
        sintesi,
        diagnosi,
        red_flags,
        priorita
    ))

    conn.commit()
    conn.close()

def get_history(patient_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM clinical_history
    WHERE patient_id=%s
    ORDER BY created_at DESC
    """, (patient_id,))

    data = c.fetchall()
    conn.close()

    return data

def mark_as_visited(request_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE requests
    SET visitato=%s,
        data_visita=%s
    WHERE id=%s
    """, (
        1,
        datetime.now().isoformat(),
        request_id
    ))

    conn.commit()
    conn.close()


def mark_as_not_visited(request_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE requests
    SET visitato=%s,
        data_visita=%s
    WHERE id=%s
    """, (
        0,
        None,
        request_id
    ))

    conn.commit()
    conn.close()


def create_user(username, password, studio_id, doctor_name, doctor_email):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO users (
        username,
        password,
        studio_id,
        doctor_name,
        doctor_email
    )
    VALUES (%s, %s, %s, %s, %s)
    """, (
        username,
        password,
        studio_id,
        doctor_name,
        doctor_email
    ))

    conn.commit()
    conn.close()

def get_doctor_by_studio(studio_id):
    conn = get_conn()
    c = conn.cursor()

    studio_id = studio_id.strip()

    c.execute("""
    SELECT doctor_name
    FROM users
    WHERE TRIM(studio_id)=%s
    """, (studio_id,))

    row = c.fetchone()
    conn.close()

    return row[0] if row else None

def get_doctor_email(studio_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT doctor_email
    FROM users
    WHERE studio_id=%s
    """, (studio_id,))

    row = c.fetchone()

    conn.close()

    return row[0] if row else None