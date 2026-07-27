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

    value = value.encode(
        "latin-1",
        "ignore"
    ).decode(
        "latin-1"
    )

    parole = []

    for parola in value.split(" "):

        if len(parola) > 35:
            parola = " ".join(
                [
                    parola[i:i+35]
                    for i in range(0, len(parola), 35)
                ]
            )

        parole.append(parola)

    return " ".join(parole).strip()



class NovyqPDF(FPDF):

    def __init__(self, studio_name="NOVYQ dental"):
        super().__init__()
        self.studio_name = studio_name

    def header(self):

        # LOGO STUDIO
        try:
            self.image(
                "logo_studio.png",
                x=10,
                y=10,
                w=35
            )
        except:
            pass

        # TITOLO
        self.set_font(
            "Arial",
            "B",
            18
        )

        self.cell(
            0,
            10,
            self.studio_name,
            ln=True,
            align="C"
        )

        self.ln(5)

        self.line(
            10,
            self.get_y(),
            200,
            self.get_y()
        )

        self.ln(8)



    def footer(self):

        self.set_y(-15)

        self.set_font(
            "Arial",
            "I",
            8
        )

        self.cell(
            0,
            10,
            f"NOVIQ Dental - Pagina {self.page_no()}",
            align="C"
        )



def section_title(pdf, text):

    pdf.set_font(
        "Arial",
        "B",
        13
    )

    pdf.cell(
        0,
        8,
        text,
        ln=True
    )

    pdf.line(
        10,
        pdf.get_y(),
        200,
        pdf.get_y()
    )

    pdf.ln(4)



def genera_pdf(
    patient_data,
    doctor_name,
    problema,
    sintesi,
    diagnosi,
    priorita,
    photos=None
):
    pdf = NovyqPDF(
        studio_name=doctor_name
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=20
    )

    pdf.add_page()


    now = datetime.now()


    # DATI VISITA

    section_title(
        pdf,
        "DATI VISITA"
    )

    pdf.set_font(
        "Arial",
        "",
        11
    )


    for testo in [
        f"Dentista: {doctor_name}",
        f"Data: {now.strftime('%d/%m/%Y')}",
        f"Ora: {now.strftime('%H:%M')}"
    ]:

        pdf.cell(
            180,
            7,
            clean_text(testo),
            ln=True
        )


    pdf.ln(5)


    # ANAGRAFICA

    section_title(
        pdf,
        "DATI ANAGRAFICI"
    )


    dati = [

        ("Nome", patient_data.get("nome")),
        ("Cognome", patient_data.get("cognome")),
        ("Data nascita", patient_data.get("data_nascita")),
        ("Eta", patient_data.get("eta")),
        ("Codice fiscale", patient_data.get("codice_fiscale")),
        ("Luogo nascita", patient_data.get("luogo_nascita")),
        ("Residenza", patient_data.get("residenza")),
        ("Telefono", patient_data.get("telefono")),
        ("Email", patient_data.get("email"))

    ]


    for label,value in dati:

        pdf.cell(
            180,
            7,
            f"{label}: {clean_text(value)}",
            ln=True
        )


    pdf.ln(5)


    # TRIAGE

    section_title(
        pdf,
        "VALUTAZIONE CLINICA"
    )

    if isinstance(problema, dict):
        problema = problema.get("answer", "")

    pdf.set_x(10)

    pdf.multi_cell(
        190,
        7,
        "Motivo visita: " + clean_text(problema)
    )

    pdf.set_x(10)

    pdf.multi_cell(
        190,
        7,
        "Priorita clinica: " + clean_text(priorita)
    )


    pdf.ln(5)


    # IPOTESI

    section_title(
        pdf,
        "IPOTESI CLINICA"
    )


    pdf.multi_cell(
        180,
        7,
        clean_text(diagnosi)
        if diagnosi
        else "Nessuna ipotesi disponibile"
    )


    pdf.ln(5)


    # QUESTIONARIO

    section_title(
        pdf,
        "QUESTIONARIO ANAMNESTICO"
    )

    pdf.set_font(
        "Arial",
        "",
        11
    )

    numero = 1

    if isinstance(sintesi, dict):

        for item in sintesi.values():

            if isinstance(item, dict):
                domanda = clean_text(
                    item.get("question", "")
                )

                risposta = clean_text(
                    item.get("answer", "")
                )

                # DOMANDA

                pdf.set_x(10)

                pdf.set_font(
                    "Arial",
                    "B",
                    11
                )

                pdf.multi_cell(
                    190,
                    7,
                    f"{numero}. {domanda}"
                )

                # RISPOSTA

                pdf.set_x(10)

                pdf.set_font(
                    "Arial",
                    "",
                    11
                )

                pdf.multi_cell(
                    190,
                    7,
                    f"Risposta: {risposta}"
                )

                pdf.ln(4)

                numero += 1

    # FOTO PAZIENTE

    if photos:

        section_title(
            pdf,
            "DOCUMENTAZIONE FOTOGRAFICA"
        )

        pdf.set_font(
            "Arial",
            "",
            11
        )

        for foto in photos:

            try:

                pdf.image(
                    foto,
                    x=20,
                    w=70
                )

                pdf.ln(5)

            except Exception as e:
                print("Errore caricamento foto PDF:", e)


    nome_file = (
        clean_text(patient_data.get("nome",""))
        +
        "_"
        +
        clean_text(patient_data.get("cognome",""))
    )


    nome_file = nome_file.replace(" ","_")

    pdf_folder = "uploads/pdfs"

    os.makedirs(
        pdf_folder,
        exist_ok=True
    )

    filename = (
        f"referto_{nome_file}_"
        f"{now.strftime('%Y%m%d%H%M%S')}.pdf"
    )

    path = os.path.join(
        pdf_folder,
        filename
    )

    pdf.output(path)

    print("PDF CREATO:", path)

    url_pdf = upload_pdf(
        path,
        filename
    )

    print("PDF ONLINE:", url_pdf)

    return url_pdf