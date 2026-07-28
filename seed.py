from db import get_conn

USERS = [

    (
        "francesco.tartari",
        "1687",
        "dr-francesco-tartari",
        "Dr. Francesco Tartari"
    ),

    (
        "iacopo.malandrucco",
        "5191",
        "dr-iacopo-malandrucco",
        "Dr. Iacopo Malandrucco"
    ),

    (
        "niccolo.leonardini",
        "1234",
        "dr-niccolo-leonardini",
        "Dr. Niccolò Leonardini"
    ),

    (
        "alessandro.contese",
        "4862",
        "studio-dentistico-contese",
        "Studio dentistico Contese"
    ),
#    (
#        "marco.rossi",
#        "7890",
#        "dr-marco-rossi",
#        "Dr. Marco Rossi"
#    ),

]

PATIENT_URL = "https://novadent-js9a9zgvfo9u5lzrwo5b5r.streamlit.app/"
DOCTOR_URL = "https://novadent-8yqxzxchmfh5z8fk44ychs.streamlit.app/"

conn = get_conn()
c = conn.cursor()

print("\n===== NOVADENT STUDIO LINKS =====\n")

for user in USERS:

    username, password, studio_id, doctor_name = user

    c.execute("""
    INSERT INTO users
    (username,password,studio_id,doctor_name)
    VALUES (%s,%s,%s,%s)
    ON CONFLICT (username) DO NOTHING
    """, user)

    patient_link = f"{PATIENT_URL}/?studio={studio_id}"
    doctor_link = DOCTOR_URL

    print(f"""
    👨‍⚕️ {doctor_name}

    🔑 Login dottore:
    Username: {username}
    Password: {password}

    🦷 Link paziente:
    {patient_link}

    👨‍⚕️ Link dottore:
    {doctor_link}
    """)

conn.commit()
conn.close()

print("\n=================================\n")
print("Seed completato")