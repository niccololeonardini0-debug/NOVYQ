import json
from datetime import date, datetime
from db import (
    insert_request,
    save_signature,
    init_db
)
from db import get_doctor_by_studio, get_doctor_email
from triage_engine import calcola_priorita
from pdf_engine import genera_pdf
from email_service import send_notification_email
from core import next_node
import os
import base64
import streamlit as st

st.set_page_config(
    page_title="Novyq Dental",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

#init_db()

# =========================
# STUDIO DA URL (compatibile e stabile)
# =========================

studio_id = None

# 1) prova formato /dr-mario-rossi
query_params = st.query_params

if len(query_params) == 1 and list(query_params.keys())[0] == "studio":
    studio_id = query_params.get("studio")

# 2) fallback classico ?studio=
if studio_id is None:
    studio_id = query_params.get("studio")

# 3) fallback assoluto
if not studio_id:
    studio_id = "default"

# pulizia
studio_id = studio_id.strip("/")

st.session_state["studio_id"] = studio_id

# =========================
# FLOW
# =========================
with open("flow.json", "r", encoding="utf-8") as f:
    FLOW = json.load(f)

PROBLEM_MAP = {
    "Dolore": [
        "pain_1","pain_2","pain_3","pain_4","pain_5","pain_6","pain_7","pain_8",
        "pain_9","pain_10","pain_11","pain_12","pain_13","pain_14","pain_15",
        "pain_16","pain_17","pain_18","pain_19","pain_20"
    ],

    "Gonfiore": [
        "sw_1","sw_2","sw_3","sw_4","sw_5","sw_6","sw_7","sw_8","sw_9",
        "sw_10","sw_11","sw_12","sw_13","sw_14","sw_15","sw_16","sw_17"
    ],

    "Trauma": [
        "tr_1","tr_2","tr_3","tr_4","tr_5","tr_6","tr_7","tr_8","tr_9",
        "tr_10","tr_11","tr_12","tr_13","tr_14","tr_15","tr_16","tr_17","tr_18"
    ],

    "Dente rotto": [
        "broken_1","broken_2","broken_3","broken_4","broken_5","broken_6",
        "broken_7","broken_8","broken_9","broken_10","broken_11","broken_12",
        "broken_13"
    ],

    "Otturazione o corona saltata": [
        "rest_1","rest_2","rest_3","rest_4","rest_5","rest_5b","rest_6",
        "rest_7","rest_8","rest_9","rest_10","rest_11","rest_11b",
        "rest_12","rest_13"
    ],

    "Sanguinamento gengivale": [
        "paro_1","paro_2","paro_3","paro_4","paro_5","paro_6","paro_7",
        "paro_8","paro_9","paro_10","paro_11","paro_12","paro_13",
        "paro_14","paro_15","paro_16","paro_17","paro_18"
    ],

    "Gengive o denti mobili": [
        "paro_1","paro_2","paro_3","paro_4","paro_5","paro_6","paro_7",
        "paro_8","paro_9","paro_10","paro_11","paro_12","paro_13",
        "paro_14","paro_15","paro_16","paro_17","paro_18"
    ],

    "Problema con impianto": [
        "imp_1","imp_2","imp_3","imp_4","imp_5","imp_6","imp_7","imp_8",
        "imp_9","imp_10","imp_11","imp_12","imp_13","imp_14","imp_15",
        "imp_16","imp_17"
    ],

    "Problema con apparecchio ortodontico": [
        "ortho_1","ortho_2","ortho_3","ortho_4","ortho_5","ortho_6",
        "ortho_7","ortho_8","ortho_9","ortho_10","ortho_11","ortho_12",
        "ortho_13"
    ],

    "Dente mancante / Protesi": [
        "prost_1","prost_2","prost_3","prost_4","prost_5","prost_6",
        "prost_7","prost_8","prost_9","prost_10","prost_11","prost_12",
        "prost_13","prost_14","prost_15"
    ],

    "Estetica": [
        "est_1","est_2","est_3","est_4","est_5","est_6","est_7","est_8","est_9"
    ],

    "Pulizia dei denti": [
        "clean_1","clean_2","clean_3","clean_4","clean_5","clean_6","clean_7"
    ],

    "Controllo": [
        "check_1","check_2","check_3","check_4","check_5"
    ],

    "Altro": [
        "other_1","other_2","other_3","other_4","other_5"
    ]
}

def is_last_node(node_id):
    next_n = next_node(node_id, None)
    return next_n in ["completed", None, "", node_id]
# =========================
# SESSION INIT
# =========================
if "node" not in st.session_state:
    st.session_state.node = "patient_info"

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}

if "question_path" not in st.session_state:
    st.session_state.question_path = []


from db import get_doctor_by_studio

doctor_name = get_doctor_by_studio(studio_id)

doctor_email = get_doctor_email(studio_id)

if not doctor_name:
    doctor_name = "Studio Odontoiatrico"

st.markdown(
    f"""
    <div style="
        text-align:center;
        font-size:64px;
        font-weight:800;
        color:#0B1F3A;
        margin-top:10px;
        margin-bottom:20px;
    ">
        {doctor_name}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<div style="
    text-align:center;
    font-size:20px;
    font-weight:700;
    color:#0F766E;
    margin-bottom:25px;
">
    NOVYQ Dental - Questionario clinico pre-visita
</div>
""", unsafe_allow_html=True)

# =========================
# CSS PULITO E STABILE
# =========================
st.markdown("""
<style>

/* CONTAINER */

.block-container{
    padding-top:1.5rem;
    padding-left:1rem;
    padding-right:1rem;
    max-width:100%;
}

/* Titolo domanda */

.question{
    font-size:28px;
    font-weight:700;
    margin-bottom:25px;
}

.stTextInput input,
.stNumberInput input{

    border-radius:12px;
    font-size:18px;
}


/* RADIO */

.stRadio label{
    font-size:17px;
}

/* SLIDER */

.stSlider{
    padding-top:10px;
    padding-bottom:15px;
}

/* BOTTONI */

.stButton>button{

    width:100%;
    height:54px;

    border-radius:12px;

    font-size:18px;
    font-weight:700;

}

/* footer */

.novadent-footer{

    position:fixed;

    right:25px;
    bottom:18px;

    opacity:.45;

    font-size:13px;

}
.novadent-footer img{

    width:130px;

}

/* Nasconde header */

header{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)


def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

logo = get_base64_image("assets/novyq_dental_logo.png")

st.markdown(
    f"""
    <div class="novadent-footer">
        <img src="data:image/png;base64,{logo}">
    </div>
    """,
    unsafe_allow_html=True
)
# =========================
# HEADER
# =========================

# =========================
# ROUTING
# =========================
node = st.session_state.node

# =========================
# PATIENT INFO
# =========================
if node == "patient_info":

    st.markdown("""
    <div style="
        text-align:center;
        font-size:26px;
        font-weight:700;
        margin-top:20px;
        color:#0B1F3A
    ">
    Benvenuto
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        text-align:center;
        font-size:17px;
        margin-top:15px;
        margin-bottom:10px;
    ">
    Per consentire al medico di conoscere al meglio la sua situazione clinica,
    le chiediamo di compilare un breve questionario.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        text-align:center;
        color:#6b7280;
        margin-bottom:30px;
    ">
    Tempo di compilazione: circa 5 minuti.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    nome = st.text_input("Nome", key="nome_input")

    cognome = st.text_input("Cognome", key="cognome_input")

    data_nascita = st.text_input(
        "Data di nascita (GG/MM/AAAA)",
        placeholder="es. 01/01/2001"
    )

    codice_fiscale = st.text_input("Codice fiscale")

    luogo_nascita = st.text_input(
        "Luogo di nascita",
        placeholder="es. Firenze, Italia"
    )

    residenza = st.text_input(
        "Residenza",
        placeholder="es. Via Roma 25, Firenze"
    )

    telefono = st.text_input(
        "Telefono",
        placeholder="es. 333 1234567"
    )

    email = st.text_input(
        "Email",
        placeholder="es. nome.cognome@email.it"
    )

    if st.button("Inizia il questionario"):

        if (
                nome.strip() == ""
                or cognome.strip() == ""
                or codice_fiscale.strip() == ""
                or luogo_nascita.strip() == ""
                or residenza.strip() == ""
                or telefono.strip() == ""
                or email.strip() == ""
        ):
            st.error("Compila tutti i campi.")
            st.stop()

            if "@" not in email or "." not in email:
                st.error("Inserisci un indirizzo email valido.")
                st.stop()

            telefono_pulito = telefono.replace(" ", "")

            if not telefono_pulito.isdigit():
                st.error("Inserisci un numero di telefono valido.")
                st.stop()
        try:
            data_nascita_obj = datetime.strptime(
                data_nascita,
                "%d/%m/%Y"
            )

            oggi = date.today()

            eta = (
                    oggi.year
                    - data_nascita_obj.year
                    - (
                            (oggi.month, oggi.day)
                            < (data_nascita_obj.month, data_nascita_obj.day)
                    )
            )

        except:
            st.error("Inserisci la data nel formato GG/MM/AAAA")
            st.stop()

        st.session_state.patient_data = {
            "nome": nome,
            "cognome": cognome,
            "data_nascita": data_nascita,
            "eta": eta,
            "codice_fiscale": codice_fiscale,
            "luogo_nascita": luogo_nascita,
            "residenza": residenza,
            "telefono": telefono,
            "email": email
        }

        st.session_state.answers = {}
        st.session_state.node = "root"
        st.rerun()

# =========================
# COMPLETED
# =========================
elif node == "completed":

    st.success("Questionario completato")

    st.markdown("### 📷 Fotografie (opzionale)")

    uploaded_photos = st.file_uploader(
        "Carica fotografie utili per il dentista",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_photos:

        if len(uploaded_photos) > 4:
            st.warning("Puoi caricare massimo 4 fotografie.")
            st.stop()

        photo_folder = "uploads/photos"

        os.makedirs(photo_folder, exist_ok=True)

        saved_photos = []

        for i, photo in enumerate(uploaded_photos):
            file_path = os.path.join(
                photo_folder,
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}_{photo.name}"
            )

            with open(file_path, "wb") as f:
                f.write(photo.getbuffer())

            saved_photos.append(file_path)

        st.session_state["photos"] = saved_photos

        st.success(f"{len(saved_photos)} fotografie caricate")

    st.markdown("---")

    st.markdown("""
    ### Informativa Privacy

    I dati personali e sanitari inseriti nel presente questionario saranno trasmessi esclusivamente allo studio odontoiatrico presso il quale è stata richiesta la visita e utilizzati per finalità di assistenza sanitaria.

    Novyq fornisce esclusivamente la piattaforma informatica utilizzata per la raccolta e la gestione dei dati.

    Proseguendo dichiari di aver letto l'informativa e autorizzi l'invio dei dati allo studio.
    """)

    consenso = st.checkbox(
        "Ho letto l'informativa privacy e autorizzo il trattamento dei miei dati."
    )

    firma = st.text_input(
        "Firma",
        placeholder="Nome e Cognome"
    )

    st.caption(
        "Digitando il tuo nome e cognome confermi la tua identità, "
        "dichiari che le informazioni inserite sono corrette e "
        "autorizzi il loro invio allo studio odontoiatrico."
    )

    if not consenso:
        st.warning("Devi accettare il consenso per inviare il questionario.")
        st.stop()

    if firma.strip() == "":
        st.warning("Inserisci la firma prima di inviare il questionario.")
        st.stop()

    if st.button("Confermo firma e invio") and "saved" not in st.session_state:
        st.session_state.patient_data["firma"] = firma

        patient = st.session_state.patient_data
        nome = f"{patient['nome']} {patient['cognome']}"
        eta = patient["eta"]

        answers = st.session_state.get("answers", {})
        studio_id = st.session_state.get("studio_id", "default")

        risultato = calcola_priorita(answers)

        priorita = risultato["priorita"]
        score = risultato["score"]
        red_flags = risultato["red_flags"]
        ipotesi = risultato["ipotesi"]
        compatibilita = risultato["compatibilita"]
        diagnosi_differenziali = risultato["diagnosi_differenziali"]
        motivi_principali = risultato["motivi_principali"]
        motivi_differenziali = risultato["motivi_differenziali"]
        report_ai = risultato["report_ai"]

        ai_report = risultato

        pdf_path = genera_pdf(
            patient_data=patient,
            doctor_name=doctor_name,
            problema=answers.get("root", {}).get("answer", "Non specificato"),
            sintesi=answers,
            diagnosi=ipotesi,
            priorita=priorita,
            compatibilita=compatibilita,
            diagnosi_differenziali=diagnosi_differenziali,
            motivi_principali=motivi_principali,
            motivi_differenziali=motivi_differenziali,
            report_ai=report_ai,
            photos=st.session_state.get("photos", [])
        )

        request_id = insert_request(
            patient,
            studio_id,
            answers=answers,
            ai_report=ai_report,
            pdf_path=pdf_path,
            consenso_privacy=True,
            data_consenso=datetime.now().isoformat()
        )

        save_signature(
            request_id,
            firma
        )

        send_notification_email(
            patient_name=nome,
            symptoms=answers.get("root", {}).get("answer", "Non specificato"),
            priority=priorita,
            doctor_email=doctor_email
        )

        st.session_state.saved = True

        st.success("Questionario inviato correttamente al dottore.")
        st.info("Il medico riceverà la documentazione per la valutazione.")

# =========================
# FLOW ENGINE
# =========================
elif node in FLOW:

    flow = FLOW[node]

    answered = sum(
        1 for x in st.session_state.answers
        if x in st.session_state.question_path
    )

    total_questions = len(st.session_state.question_path)

    if total_questions > 0:
        progress = min(answered / total_questions, 1)
    else:
        progress = 0

    st.progress(progress)
    current = min(answered + 1, total_questions)

    st.caption(f"Domanda {current} di {total_questions}")

    st.caption("Compilazione questionario clinico")

    st.write("")

    st.markdown(f"<div class='question'>{flow['question']}</div>", unsafe_allow_html=True)

    # INPUT
    if flow.get("type") == "multiselect":

        answer = []

        st.caption("Seleziona il motivo principale della visita")

        for option in flow.get("options", []):

            if st.checkbox(
                    option,
                    key=f"{node}_{option}"
            ):
                answer.append(option)

        if len(answer) > flow.get("max_selections", 1):
            st.error("Puoi selezionare massimo 1 problema.")


    elif flow.get("type") == "radio":

        answer = st.radio(
            "",
            flow.get("options", []),
            key=node
        )


    elif flow.get("type") == "slider":

        answer = st.slider("", 0, 10, 5, key=node)


    elif flow.get("type") == "group":

        answer = {}

        for field in flow.get("fields", []):

            st.markdown(

                f"<div class='question'>{field['question']}</div>",

                unsafe_allow_html=True

            )

            if field["type"] == "radio":

                answer[field["question"]] = st.radio(

                    "",

                    field.get("options", []),

                    key=f"{node}_{field['question']}"

                )


            elif field["type"] == "text":

                answer[field["question"]] = st.text_input(

                    "",

                    key=f"{node}_{field['question']}"

                )


    else:

        answer = st.text_input("", key=node, placeholder=flow["question"])

    # =========================
    # BUTTON LABEL LOGIC
    # =========================
    next_n = next_node(node, answer)

    if node == "patient_info":
        button_label = "Inizia questionario"
    elif next_n == "completed":
        button_label = "Invia al dentista"
    else:
        button_label = "Avanti"

    # =========================
    # BUTTON ACTION
    # =========================
    if st.button(button_label):

        st.session_state.answers[node] = {
            "question": flow.get("question"),
            "answer": answer
        }

        if node == "prost_5":
            if str(answer).strip().lower() == "nessuna protesi":
                for n in ["prost_8", "prost_9", "prost_10"]:
                    if n in st.session_state.question_path:
                        st.session_state.question_path.remove(n)

        if node == "imp_13":
            if str(answer).strip().lower() == "no":
                if "imp_14" in st.session_state.question_path:
                    st.session_state.question_path.remove("imp_14")

        if node == "sw_14":
            if str(answer).strip().lower() == "no":
                if "sw_15" in st.session_state.question_path:
                    st.session_state.question_path.remove("sw_15")

        if node == "imp_4":
            imp4 = str(answer).strip().lower()
            if imp4 in ["meno di 1 mese", "1-6 mesi"]:
                if "imp_15" in st.session_state.question_path:
                    st.session_state.question_path.remove("imp_15")

        if node == "imp_4":
            imp4 = str(answer).strip().lower()

            if imp4 in ["meno di 1 mese", "1-6 mesi"]:
                if "imp_15" in st.session_state.question_path:
                    st.session_state.question_path.remove("imp_15")
            else:
                if "imp_15" not in st.session_state.question_path:
                    idx = st.session_state.question_path.index("imp_14") + 1
                    st.session_state.question_path.insert(idx, "imp_15")

        # SCELTA PROBLEMI
        if node == "root":

            answer = str(answer).strip()

            if not answer:
                st.error("Seleziona un problema.")
                st.stop()

            if answer not in PROBLEM_MAP:
                st.error(f"Problema non riconosciuto: {answer}")
                st.stop()

            percorso = PROBLEM_MAP[answer].copy()

            percorso.extend([
                "med_extra",
                "med_1",
                "med_2",
                "med_3",
                "med_4",
                "med_5",
                "med_6",
                "med_7"
            ])

            st.session_state.question_path = percorso
            st.session_state.node = percorso[0]


        else:

            if node in st.session_state.question_path:

                posizione = st.session_state.question_path.index(node)

                if posizione + 1 < len(st.session_state.question_path):
                    st.session_state.node = st.session_state.question_path[posizione + 1]
                else:
                    st.session_state.node = "completed"

            else:
                st.session_state.node = next_n

        st.rerun()

else:
    st.error(f"Nodo non trovato: {node}")

