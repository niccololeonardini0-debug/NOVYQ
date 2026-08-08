from db import (
    login,
    get_requests,
    init_db,
    mark_as_visited,
    mark_as_not_visited
)
import json
from datetime import datetime
from db import save_doctor_note
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

#init_db()

st.set_page_config(page_title="Novyq Doctor", layout="wide")

# =========================
# SESSION
# =========================
if "doctor_logged" not in st.session_state:
    st.session_state.doctor_logged = False


# =========================
# LOGIN
# =========================
if not st.session_state.doctor_logged:

    st.markdown(
        """
        <div style="
            text-align:left;
            font-family:'Inter','Arial',sans-serif;
            font-size:15px;
            font-weight:900;
            color:#64748B;
            margin-top:15px;
            margin-bottom:35px;
        ">
            Doctor Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
        text-align:center;
        font-family:'Inter','Arial',sans-serif;
        font-size:56px;
        font-weight:900;
        letter-spacing:-1.5px;
        color:#111827
        margin-top:20px;
        margin-bottom:10px;
        ">
        Archivio questionari
        </div>

        <div style="
        text-align:center;
        font-family:'Inter','Arial',sans-serif;
        font-size:24px;
        font-weight:700;
        color:#0F766E;
        margin-bottom:15px;
        ">
        NOVYQ Dental
        </div>

        <div style="
        text-align:center;
        font-family:'Inter','Arial',sans-serif;
        font-size:15px;
        font-weight:500;
        color:#64748B;
        margin-bottom:40px;
        max-width:760px;
        margin-left:auto;
        margin-right:auto;
        line-height:1.6;
        ">
        Piattaforma di pre-visita odontoiatrica che raccoglie informazioni anamnestiche e cliniche prima dell'appuntamento, offrendo al dentista un supporto per la valutazione iniziale del paziente.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
        text-align:center;
        font-family:'Inter','Arial',sans-serif;
        font-size:15px;
        color:#64748B;
        margin-bottom:20px;
        ">
        Accesso riservato allo studio odontoiatrico
        </div>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Accedi"):

        user = login(username, password)

        if user:
            st.session_state.doctor_logged = True
            st.session_state.username = username
            st.session_state.studio_id = user[2].strip("/")
            st.session_state.doctor_name = user[3]
            st.rerun()

        else:
            st.error("Accesso non riuscito. Verifica le credenziali inserite.")

    st.stop()
# =========================
# HEADER
# =========================

st.markdown(
    """
    <div style="
        text-align:left;
        font-family:'Inter','Arial',sans-serif;
        font-size:15px;
        font-weight:600;
        color:#64748B;
        margin-top:15px;
        margin-bottom:45px;
    ">
        Doctor Dashboard
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"""
    <div style="
        text-align:center;
        font-family:'Palatino Linotype','Book Antiqua',Palatino,serif;
        font-size:clamp(40px,8vw,64px);
        font-weight:1000;
        color:#0B1F3A;
        letter-spacing:1px;
        margin-top:15px;
        margin-bottom:15px;
        text-shadow:0px 2px 4px rgba(0,0,0,0.12);
    ">
        {st.session_state.doctor_name}
    </div>

    <div style="
        text-align:center;
        font-family:'Inter','Arial',sans-serif;
        font-size:22px;
        font-weight:700;
        color:#167D5A;
        margin-bottom:45px;
    ">
        Pre-visite odontoiatriche
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()
# =========================
# LOAD REQUESTS
# =========================

requests = get_requests(st.session_state.studio_id)

priorita_order = {
    "ALTA": 0,
    "MEDIA": 1,
    "BASSA": 2
}

requests = sorted(
    requests,
    key=lambda r: (
        r[9],  # non visitati prima
        priorita_order.get(
            json.loads(r[6]).get("priorita", "BASSA")
            if r[6] else "BASSA",
            2
        ),
        -datetime.fromisoformat(str(r[7])).timestamp()
        if r[7] else 0
    )
)

if not requests:
    st.info("Nessuna richiesta presente")
    st.stop()

# =========================
# RICERCA PAZIENTE
# =========================

search = st.text_input(
    "🔎 Cerca paziente",
    placeholder="Nome e cognome"
)

if search:

    search = search.lower().strip()

    requests = [
        r for r in requests
        if search in f"{r[1]} {r[2]}".lower()
    ]



# =========================
# LISTA PAZIENTI
# =========================

for r in requests:

    patient_id = r[0]
    visitato = r[9]

    nome = r[1]
    cognome = r[2]
    eta = r[3]
    motivo = r[4]
    data_richiesta = r[7]

    try:
        data_richiesta = datetime.fromisoformat(
            str(data_richiesta)
        ).strftime("%d/%m/%Y %H:%M")
    except:
        pass

    try:
        ai_report = json.loads(r[6]) if r[6] else {}
        doctor_note = r[10] if len(r) > 10 else ""
    except:
        ai_report = {}
        doctor_note = ""

    priorita = ai_report.get("priorita", "BASSA")
    ipotesi = ai_report.get("ipotesi", "—")

    # =========================
    # CARD PAZIENTE
    # =========================

    with st.container(border=True):

        # TESTATA
        header_col1, header_col2 = st.columns([4, 1])

        with header_col1:
            st.markdown(
                f"### {nome} {cognome}"
            )

            st.caption(
                f"{eta} anni"
            )

        with header_col2:

            if priorita == "ALTA":
                st.error("🔴 ALTA")

            elif priorita == "MEDIA":
                st.warning("🟡 MEDIA")

            else:
                st.success("🟢 BASSA")

        # =========================
        # INFORMAZIONI
        # =========================

        info1, info2, info3, info4 = st.columns(4)

        with info1:
            st.caption("MOTIVO")
            st.write(
                motivo if motivo else "—"
            )

        with info2:
            st.caption("IPOTESI CLINICA")
            st.write(
                ipotesi
            )

        with info3:
            st.caption("DATA E ORA")
            st.write(
                data_richiesta
            )

        with info4:
            st.caption("STATO")

            if visitato == 0:
                st.write("🔵 Da visitare")
            else:
                st.write("🟢 Visitato")

        # =========================
        # AZIONI
        # =========================

        st.markdown("")

        action1, action2, action3 = st.columns(
            [1, 1, 3]
        )

        with action1:

            pdf_url = r[8]

            if pdf_url:
                st.link_button(
                    "📄 PDF",
                    pdf_url,
                    use_container_width=True
                )

        with action2:

            if visitato == 0:

                if st.button(
                    "✅ Visitato",
                    key=f"visit_{patient_id}",
                    use_container_width=True
                ):
                    mark_as_visited(patient_id)
                    st.rerun()

            else:

                if st.button(
                    "↩️ Non visitato",
                    key=f"unvisit_{patient_id}",
                    use_container_width=True
                ):
                    mark_as_not_visited(patient_id)
                    st.rerun()

        # =========================
        # NOTE
        # =========================

        with st.expander("📝 Note del dentista"):

            note = st.text_area(
                "Scrivi una nota",
                value=doctor_note or "",
                key=f"note_{patient_id}",
                height=120
            )

            if st.button(
                "Salva nota",
                key=f"save_note_{patient_id}"
            ):
                save_doctor_note(
                    patient_id,
                    note
                )

                st.success("Nota salvata")
                st.rerun()

    st.markdown(
        "<div style='height:6px'></div>",
        unsafe_allow_html=True
    )

import base64

def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


logo = get_base64_image("assets/novyq_dental_logo.png")


st.markdown(
    f"""
    <div style="
        position:fixed;
        right:18px;
        bottom:12px;
        opacity:0.45;
    ">
        <img src="data:image/png;base64,{logo}" width="130">
    </div>
    """,
    unsafe_allow_html=True
)