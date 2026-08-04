from fpdf import FPDF
from datetime import datetime
import os
from supabase_storage import upload_pdf


def clean_text(value):
    if value is None:
        return ""

    value = str(value)
    value = (
        value
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("\t", " ")
    )

    value = value.encode("latin-1", "ignore").decode("latin-1")

    parole = []
    for parola in value.split(" "):
        if len(parola) > 35:
            parola = " ".join(
                [
                    parola[i:i + 35]
                    for i in range(0, len(parola), 35)
                ]
            )
        parole.append(parola)

    return " ".join(parole).strip()


def format_answer(answer):
    if answer is None:
        return ""

    if isinstance(answer, list):
        return ", ".join(str(x) for x in answer if str(x).strip())

    if isinstance(answer, dict):
        parti = []
        for k, v in answer.items():
            testo_v = format_answer(v)
            if testo_v:
                parti.append(f"{k}: {testo_v}")
        return "; ".join(parti)

    return clean_text(answer)


class NovyqPDF(FPDF):
    def __init__(self, studio_name="NOVYQ dental"):
        super().__init__()
        self.studio_name = studio_name

    def header(self):
        try:
            self.image("logo_studio.png", x=10, y=10, w=35)
        except:
            pass

        self.set_font("Arial", "B", 18)
        self.cell(0, 10, self.studio_name, ln=True, align="C")
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"NOVIQ Dental - Pagina {self.page_no()}", align="C")


def section_title(pdf, text):
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, text, ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)


def write_heading(pdf, text):
    pdf.set_x(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, text, ln=True)
    pdf.set_font("Arial", "", 11)


def write_bullets(pdf, items, limit=None):
    if not items:
        return

    if limit is not None:
        items = items[:limit]

    for item in items:
        pdf.set_x(10)
        pdf.multi_cell(0, 7, f"- {clean_text(item)}")


def genera_pdf(
    patient_data,
    doctor_name,
    problema,
    sintesi,
    diagnosi,
    priorita,
    compatibilita=None,
    diagnosi_differenziali=None,
    motivi_principali=None,
    motivi_differenziali=None,
    report_ai=None,
    photos=None
):
    pdf = NovyqPDF(studio_name=doctor_name)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(10, 10, 10)
    pdf.add_page()

    now = datetime.now()

    # DATI VISITA
    section_title(pdf, "DATI VISITA")
    pdf.set_font("Arial", "", 11)

    for testo in [
        f"Dentista: {doctor_name}",
        f"Data: {now.strftime('%d/%m/%Y')}",
        f"Ora: {now.strftime('%H:%M')}"
    ]:
        pdf.cell(180, 7, clean_text(testo), ln=True)

    pdf.ln(5)

    # ANAGRAFICA
    section_title(pdf, "DATI ANAGRAFICI")

    dati = [
        ("Nome", patient_data.get("nome")),
        ("Cognome", patient_data.get("cognome")),
        ("Data nascita", patient_data.get("data_nascita")),
        ("Eta", patient_data.get("eta")),
        ("Codice fiscale", patient_data.get("codice_fiscale")),
        ("Luogo nascita", patient_data.get("luogo_nascita")),
        ("Residenza", patient_data.get("residenza")),
        ("Telefono", patient_data.get("telefono")),
        ("Email", patient_data.get("email")),
    ]

    pdf.set_font("Arial", "", 11)
    for label, value in dati:
        pdf.set_x(10)
        pdf.multi_cell(0, 7, f"{label}: {clean_text(value)}")

    pdf.ln(5)

    # VALUTAZIONE CLINICA
    section_title(pdf, "VALUTAZIONE CLINICA")

    if isinstance(problema, dict):
        problema = problema.get("answer", "")

    pdf.set_x(10)
    pdf.multi_cell(0, 7, "Motivo visita: " + clean_text(problema))

    pdf.set_x(10)
    pdf.multi_cell(0, 7, "Priorita clinica: " + clean_text(priorita))

    pdf.ln(4)

    # DIAGNOSI PRINCIPALE
    write_heading(pdf, "DIAGNOSI PRINCIPALE")

    if diagnosi:
        testo = clean_text(diagnosi)
        if isinstance(compatibilita, dict) and diagnosi in compatibilita:
            testo = f"{testo} ({compatibilita[diagnosi]})"
        pdf.set_x(10)
        pdf.multi_cell(0, 7, testo)
    else:
        pdf.set_x(10)
        pdf.multi_cell(0, 7, "Non determinabile")

    pdf.ln(3)

    # MOTIVI
    if motivi_principali:
        write_heading(pdf, "MOTIVI")
        write_bullets(pdf, motivi_principali, limit=8)
        pdf.ln(2)

    # DIAGNOSI DIFFERENZIALI
    if diagnosi_differenziali:
        write_heading(pdf, "DIAGNOSI DIFFERENZIALI/POSSIBILI CONDIZIONI CONCOMITANTI")

        for d in diagnosi_differenziali:
            pdf.set_x(10)
            pdf.multi_cell(0, 7, f"- {clean_text(d)}")

            if motivi_differenziali and d in motivi_differenziali and motivi_differenziali[d]:
                pdf.set_x(10)
                pdf.set_font("Arial", "B", 11)
                pdf.multi_cell(0, 7, "Motivi:")
                pdf.set_font("Arial", "", 11)

                for motivo in motivi_differenziali[d][:2]:
                    pdf.set_x(10)
                    pdf.multi_cell(0, 7, f"  - {clean_text(motivo)}")

        pdf.ln(2)

    # RISPOSTE COMPLETE
    section_title(pdf, "RISPOSTE COMPLETE DEL PAZIENTE")
    pdf.set_font("Arial", "", 11)

    numero = 1
    if isinstance(sintesi, dict):
        for item in sintesi.values():
            if not isinstance(item, dict):
                continue

            domanda = clean_text(item.get("question", ""))
            risposta_raw = item.get("answer", "")
            risposta = format_answer(risposta_raw)

            pdf.set_x(10)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 7, f"{numero}. {domanda}")

            pdf.set_x(10)
            pdf.set_font("Arial", "", 11)

            if isinstance(risposta_raw, dict):
                for sub_domanda, sub_risposta in risposta_raw.items():
                    pdf.set_x(10)
                    pdf.multi_cell(0, 7, f"- {clean_text(sub_domanda)}: {clean_text(sub_risposta)}")
            else:
                pdf.multi_cell(0, 7, f"Risposta: {clean_text(risposta)}")

            pdf.ln(4)
            numero += 1

    # FOTO PAZIENTE
    if photos:
        section_title(pdf, "DOCUMENTAZIONE FOTOGRAFICA")
        pdf.set_font("Arial", "", 11)

        for foto in photos:
            try:
                pdf.image(foto, x=20, w=70)
                pdf.ln(5)
            except Exception as e:
                print("Errore caricamento foto PDF:", e)

    # CONSENSO E FIRMA
    pdf.add_page()

    section_title(pdf, "CONSENSO INFORMATO E FIRMA")
    pdf.set_font("Arial", "", 11)

    pdf.multi_cell(
        0,
        7,
        "Il paziente dichiara di aver letto l'informativa privacy e autorizza il trattamento dei dati personali ai fini della visita odontoiatrica."
    )

    pdf.ln(8)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, "Firma del paziente:", ln=True)

    pdf.ln(6)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, clean_text(patient_data.get("firma", "")))

    nome_file = (
        clean_text(patient_data.get("nome", ""))
        + "_"
        + clean_text(patient_data.get("cognome", ""))
    ).replace(" ", "_")

    pdf_folder = "uploads/pdfs"
    os.makedirs(pdf_folder, exist_ok=True)

    filename = f"referto_{nome_file}_{now.strftime('%Y%m%d%H%M%S')}.pdf"
    path = os.path.join(pdf_folder, filename)

    pdf.output(path)

    print("PDF CREATO:", path)

    url_pdf = upload_pdf(path, filename)

    print("PDF ONLINE:", url_pdf)

    return url_pdf