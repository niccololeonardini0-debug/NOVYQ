def genera_report(
    priorita,
    ipotesi,
    compatibilita,
    diagnosi_differenziali,
    motivi_principali,
    motivi_differenziali,
    answers,
    red_flags
):

    report = []

    branca = "Generale"

    if any(x in ipotesi.lower() for x in [
        "pulpite",
        "necrosi",
        "carie",
        "granuloma",
        "ascesso apicale",
        "cracked"
    ]):
        branca = "Endodonzia"

    elif any(x in ipotesi.lower() for x in [
        "gengivite",
        "parodontite",
        "parodontale"
    ]):
        branca = "Parodontologia"

    elif any(x in ipotesi.lower() for x in [
        "frattura",
        "lussazione",
        "sublussazione",
        "contusione",
        "avulsione"
    ]):
        branca = "Traumatologia"

    elif "implant" in ipotesi.lower():
        branca = "Implantologia"

    elif "ortodont" in ipotesi.lower():
        branca = "Ortodonzia"

    elif "protes" in ipotesi.lower():
        branca = "Protesi"

    elif any(x in ipotesi.lower() for x in [
        "pericoronite",
        "alveolite"
    ]):
        branca = "Chirurgia orale"

    elif "temporo" in ipotesi.lower():
        branca = "Gnatologia"

    elif "mucosa" in ipotesi.lower():
        branca = "Patologia orale"

    elif "estetica" in ipotesi.lower():
        branca = "Odontoiatria estetica"

    elif any(x in ipotesi.lower() for x in [
        "igiene",
        "controllo"
    ]):
        branca = "Prevenzione"

    report.append("REPORT DI TRIAGE ODONTOIATRICO")
    report.append("")
    report.append(f"Branca clinica: {branca}")
    report.append("")

    report.append("Ipotesi clinica principale")
    report.append("")
    report.append(f"- {ipotesi}")
    report.append(f"- Compatibilità clinica: {compatibilita.get(ipotesi, 'Bassa')}")
    report.append("")

    report.append("Motivi principali")
    if motivi_principali:
        for motivo in motivi_principali:
            report.append(f"- {motivo}")
    else:
        report.append("- Nessun elemento rilevante")
    report.append("")

    report.append("Diagnosi differenziali")
    if diagnosi_differenziali:
        for diagnosi in diagnosi_differenziali:
            report.append(f"- {diagnosi}")
            for motivo in motivi_differenziali.get(diagnosi, []):
                report.append(f"  - {motivo}")


    report.append("Domande e risposte rilevanti")
    gia_aggiunti = set()

    for dato in answers.values():
        if not isinstance(dato, dict):
            continue

        domanda = dato.get("question", "")
        risposta = str(dato.get("answer", "")).strip()

        if risposta in ["", "No", "Nessuno", "Nessuna"]:
            continue

        testo = f"{domanda}: {risposta}"
        if testo in gia_aggiunti:
            continue

        gia_aggiunti.add(testo)
        report.append(f"- {testo}")

    report.append("")

    if red_flags:
        report.append("Red flags")
        for rf in red_flags:
            report.append(f"- {rf}")
        report.append("")

    report.append(
        "Il presente report costituisce un supporto al triage e non sostituisce la valutazione clinica dell'odontoiatra."
    )

    return "\n".join(report)

def calcola_priorita(answers):

    flat_text = " ".join(
        str(v.get("answer", ""))
        for v in answers.values()
        if isinstance(v, dict)
    ).lower()

    score = 0
    ipotesi = "Non determinata"
    probabilita = 0

    diagnosi = {
        # Endodonzia
        "Carie iniziale": 0,
        "Carie profonda": 0,
        "Pulpite reversibile": 0,
        "Pulpite irreversibile": 0,
        "Necrosi pulpare": 0,
        "Granuloma apicale": 0,
        "Ascesso apicale": 0,
        "Cracked tooth syndrome": 0,

        # Conservativa / Protesi
        "Otturazione infiltrata": 0,
        "Otturazione o corona distaccata": 0,
        "Frattura dentale": 0,

        # Parodonto
        "Gengivite": 0,
        "Parodontite": 0,
        "Ascesso parodontale": 0,

        # Chirurgia orale
        "Pericoronite": 0,
        "Alveolite post-estrattiva": 0,

        # Traumatologia
        "Contusione dentale": 0,
        "Sublussazione": 0,
        "Lussazione": 0,
        "Avulsione dentale": 0,

        # Implantologia
        "Mucosite peri-implantare": 0,
        "Peri-implantite": 0,
        "Complicanza implantare": 0,

        # Ortodonzia
        "Urgenza ortodontica": 0,

        # Protesi
        "Problema protesico": 0,

        # Altre
        "Ipersensibilità dentinale": 0,
        "Disordine temporo-mandibolare": 0,
        "Lesione della mucosa orale": 0,
        "Richiesta estetica": 0,
        "Igiene professionale": 0,
        "Visita di controllo": 0
    }

    famiglie = {

        "Carie iniziale": "Endodonzia",
        "Carie profonda": "Endodonzia",
        "Pulpite reversibile": "Endodonzia",
        "Pulpite irreversibile": "Endodonzia",
        "Necrosi pulpare": "Endodonzia",
        "Granuloma apicale": "Endodonzia",
        "Ascesso apicale": "Endodonzia",
        "Cracked tooth syndrome": "Endodonzia",

        "Otturazione infiltrata": "Restaurativa",
        "Otturazione o corona distaccata": "Restaurativa",
        "Frattura dentale": "Restaurativa",

        "Gengivite": "Parodontologia",
        "Parodontite": "Parodontologia",
        "Ascesso parodontale": "Parodontologia",

        "Pericoronite": "Chirurgia orale",
        "Alveolite post-estrattiva": "Chirurgia orale",

        "Contusione dentale": "Traumatologia",
        "Sublussazione": "Traumatologia",
        "Lussazione": "Traumatologia",
        "Avulsione dentale": "Traumatologia",

        "Mucosite peri-implantare": "Implantologia",
        "Peri-implantite": "Implantologia",
        "Complicanza implantare": "Implantologia",

        "Urgenza ortodontica": "Ortodonzia",

        "Problema protesico": "Protesi",

        "Disordine temporo-mandibolare": "Gnatologia",

        "Lesione della mucosa orale": "Patologia orale",

        "Richiesta estetica": "Estetica",

        "Igiene professionale": "Prevenzione",
        "Visita di controllo": "Prevenzione"
    }

    diagnosi_differenziali = []

    red_flags = []

    motivi = {
        nome: []
        for nome in diagnosi.keys()
    }


    # ==========================
    # DOLORE
    # ==========================

    if "dolore" in flat_text:

        score += 2

        # Carie
        diagnosi["Carie iniziale"] += 1
        diagnosi["Carie profonda"] += 2

        diagnosi["Pulpite irreversibile"] += 2
        motivi["Pulpite irreversibile"].append("Dolore riferito")

        # Sensibilità
        diagnosi["Ipersensibilità dentinale"] += 1
        motivi["Ipersensibilità dentinale"].append("Sensibilità dentinale")

        # --------------------------
        # Stimoli termici
        # --------------------------

        if "freddo" in flat_text:
            diagnosi["Pulpite reversibile"] += 3
            motivi["Pulpite reversibile"].append("Dolore evocato dal freddo")

            diagnosi["Carie profonda"] += 2
            motivi["Carie profonda"].append("Dolore evocato dal freddo")

            diagnosi["Ipersensibilità dentinale"] += 3
            motivi["Ipersensibilità dentinale"].append("Sensibilità al freddo")

        if "caldo" in flat_text:
            diagnosi["Pulpite irreversibile"] += 4
            motivi["Pulpite irreversibile"].append("Dolore aggravato dal caldo")

            diagnosi["Necrosi pulpare"] += 2
            motivi["Necrosi pulpare"].append("Dolore aggravato dal caldo")

        if "dolci" in flat_text:
            diagnosi["Carie profonda"] += 3

        # --------------------------
        # Dolore spontaneo
        # --------------------------

        if "spontaneamente" in flat_text:
            diagnosi["Pulpite irreversibile"] += 4
            motivi["Pulpite irreversibile"].append("Dolore spontaneo")

        if "continuo" in flat_text:
            diagnosi["Pulpite irreversibile"] += 4
            motivi["Pulpite irreversibile"].append("Dolore continuo")

            diagnosi["Necrosi pulpare"] += 2
            motivi["Necrosi pulpare"].append("Dolore continuo")

        if "notte" in flat_text:
            diagnosi["Pulpite irreversibile"] += 5
            motivi["Pulpite irreversibile"].append("Dolore notturno")

        if "pulsante" in flat_text:
            diagnosi["Pulpite irreversibile"] += 3
            diagnosi["Ascesso apicale"] += 2

        # --------------------------
        # Masticazione
        # --------------------------

        if "masticazione" in flat_text or "mordendo" in flat_text:
            diagnosi["Cracked tooth syndrome"] += 4
            motivi["Cracked tooth syndrome"].append("Dolore durante la masticazione")

            diagnosi["Frattura dentale"] += 3
            motivi["Frattura dentale"].append("Dolore durante la masticazione")

            diagnosi["Ascesso apicale"] += 2
            motivi["Ascesso apicale"].append("Dolore durante la masticazione")
        # --------------------------
        # Intensità
        # --------------------------

        if any(x in flat_text for x in ["8", "9", "10"]):
            score += 3
            diagnosi["Pulpite irreversibile"] += 3
            motivi["Pulpite irreversibile"].append("Dolore molto intenso")

            diagnosi["Ascesso apicale"] += 2
            motivi["Ascesso apicale"].append("Dolore molto intenso")

        # --------------------------
        # Dente già curato
        # --------------------------

        if "devitalizzazione" in flat_text:
            diagnosi["Necrosi pulpare"] += 3
            motivi["Necrosi pulpare"].append("Dente già devitalizzato")

            diagnosi["Granuloma apicale"] += 2
            motivi["Granuloma apicale"].append("Dente già devitalizzato")

        if "otturazione" in flat_text:
            diagnosi["Otturazione infiltrata"] += 3
            motivi["Otturazione infiltrata"].append("Presenza di otturazione")

        if "corona" in flat_text:
            diagnosi["Otturazione o corona distaccata"] += 2
            motivi["Otturazione o corona distaccata"].append("Presenza di corona")

    # ==========================
    # GONFIORE / INFEZIONE
    # ==========================

    if "gonfiore" in flat_text:

        score += 3

        diagnosi["Ascesso apicale"] += 4
        motivi["Ascesso apicale"].append("Presenza di gonfiore")

        diagnosi["Ascesso parodontale"] += 2
        motivi["Ascesso parodontale"].append("Presenza di gonfiore")

        if "pus" in flat_text:
            diagnosi["Ascesso apicale"] += 5
            motivi["Ascesso apicale"].append("Fuoriuscita di pus")

            diagnosi["Peri-implantite"] += 3
            motivi["Peri-implantite"].append("Fuoriuscita di pus")

        if "febbre" in flat_text:
            diagnosi["Ascesso apicale"] += 4
            motivi["Ascesso apicale"].append("Febbre associata")
            score += 2
            red_flags.append("Febbre associata")

        if "guancia" in flat_text or "viso" in flat_text:
            diagnosi["Ascesso apicale"] += 3
            motivi["Ascesso apicale"].append("Gonfiore del viso")

        if "deglutire" in flat_text:
            score += 5
            red_flags.append("Difficoltà alla deglutizione")

        if "respirare" in flat_text:
            score += 8
            red_flags.append("Difficoltà respiratoria")

        if "dente del giudizio" in flat_text:
            diagnosi["Pericoronite"] += 5
            motivi["Pericoronite"].append("Coinvolgimento del dente del giudizio")

        if "impianto" in flat_text:
            diagnosi["Peri-implantite"] += 5
            motivi["Peri-implantite"].append("Sintomi localizzati su impianto")

            diagnosi["Mucosite peri-implantare"] += 3
            motivi["Mucosite peri-implantare"].append("Sintomi localizzati su impianto")

        if "mobile" in flat_text:
            diagnosi["Ascesso parodontale"] += 3
            motivi["Ascesso parodontale"].append("Mobilità dentale")

            diagnosi["Parodontite"] += 2
            motivi["Parodontite"].append("Mobilità dentale")


    # ==========================
    # TRAUMA
    # ==========================

    if "trauma" in flat_text or "caduta" in flat_text or "urto" in flat_text:

        score += 4

        diagnosi["Contusione dentale"] += 2
        motivi["Contusione dentale"].append("Trauma dentale")

        diagnosi["Sublussazione"] += 2
        motivi["Sublussazione"].append("Trauma dentale")

        diagnosi["Lussazione"] += 2
        motivi["Lussazione"].append("Trauma dentale")

        if "sport" in flat_text:
            diagnosi["Contusione dentale"] += 2
            motivi["Contusione dentale"].append("Trauma sportivo")

        if "incidente" in flat_text:
            diagnosi["Lussazione"] += 3
            motivi["Lussazione"].append("Trauma da incidente")

        if "avulsione" in flat_text or "uscito completamente" in flat_text:
            diagnosi["Avulsione dentale"] += 10
            motivi["Avulsione dentale"].append("Dente completamente fuoriuscito")
            score += 8
            red_flags.append("Avulsione dentale")

        if "spostato" in flat_text:
            diagnosi["Lussazione"] += 6
            motivi["Lussazione"].append("Dente spostato")

        if "si muove" in flat_text:
            diagnosi["Sublussazione"] += 5
            motivi["Sublussazione"].append("Mobilità dentale dopo trauma")

            diagnosi["Lussazione"] += 3
            motivi["Lussazione"].append("Mobilità dentale dopo trauma")

        if "molto" in flat_text:
            diagnosi["Lussazione"] += 2
            motivi["Lussazione"].append("Mobilità importante")

        if "frattura evidente" in flat_text:
            diagnosi["Frattura dentale"] += 6
            motivi["Frattura dentale"].append("Frattura evidente")

        if "manca una parte importante" in flat_text:
            diagnosi["Frattura dentale"] += 8
            motivi["Frattura dentale"].append("Perdita importante di struttura dentale")

        if "piccola scheggiatura" in flat_text:
            diagnosi["Frattura dentale"] += 2
            motivi["Frattura dentale"].append("Piccola scheggiatura")

        if "sensibile al freddo" in flat_text:
            diagnosi["Frattura dentale"] += 2
            motivi["Frattura dentale"].append("Sensibilità al freddo")

            diagnosi["Pulpite reversibile"] += 2
            motivi["Pulpite reversibile"].append("Sensibilità al freddo")

        if "dolore mordendo" in flat_text:
            diagnosi["Cracked tooth syndrome"] += 3
            motivi["Cracked tooth syndrome"].append("Dolore mordendo")

            diagnosi["Frattura dentale"] += 2
            motivi["Frattura dentale"].append("Dolore mordendo")

        if "sanguinamento" in flat_text:
            diagnosi["Lussazione"] += 2
            motivi["Lussazione"].append("Sanguinamento dopo trauma")

        if "gonfiore" in flat_text:
            diagnosi["Contusione dentale"] += 2
            motivi["Contusione dentale"].append("Gonfiore post-traumatico")

        if "non" in flat_text and "aprire" in flat_text:
            score += 3
            red_flags.append("Limitazione apertura bocca")

        if "perso conoscenza" in flat_text:
            score += 10
            red_flags.append("Trauma cranico associato")

    # ==========================
    # ORTODONZIA
    # ==========================

    if "apparecchio" in flat_text or "bracket" in flat_text or "mascherina" in flat_text:

        diagnosi["Urgenza ortodontica"] += 4
        motivi["Urgenza ortodontica"].append("Problema con apparecchio ortodontico")

        if "filo che punge" in flat_text:
            diagnosi["Urgenza ortodontica"] += 5
            motivi["Urgenza ortodontica"].append("Filo ortodontico che punge")

        if "bracket staccato" in flat_text:
            diagnosi["Urgenza ortodontica"] += 5
            motivi["Urgenza ortodontica"].append("Bracket distaccato")

        if "contenzione staccata" in flat_text:
            diagnosi["Urgenza ortodontica"] += 4
            motivi["Urgenza ortodontica"].append("Contenzione distaccata")

        if "mascherina rotta" in flat_text:
            diagnosi["Urgenza ortodontica"] += 3
            motivi["Urgenza ortodontica"].append("Mascherina ortodontica rotta")

        if "dolore" in flat_text:
            diagnosi["Urgenza ortodontica"] += 2
            motivi["Urgenza ortodontica"].append("Dolore correlato all'apparecchio")

        if "ferite" in flat_text or "guancia" in flat_text or "lingua" in flat_text:
            diagnosi["Urgenza ortodontica"] += 3
            motivi["Urgenza ortodontica"].append("Lesioni della mucosa causate dall'apparecchio")

        if "non" in flat_text and "indossare" in flat_text:
            diagnosi["Urgenza ortodontica"] += 4
            motivi["Urgenza ortodontica"].append("Impossibilità di indossare il dispositivo")

        if "trauma" in flat_text:
            diagnosi["Urgenza ortodontica"] += 2
            motivi["Urgenza ortodontica"].append("Trauma con apparecchio ortodontico")

    # ==========================
    # IMPLANTOLOGIA
    # ==========================

    if "impianto" in flat_text:

        diagnosi["Mucosite peri-implantare"] += 2
        motivi["Mucosite peri-implantare"].append("Presenza di impianto")

        diagnosi["Peri-implantite"] += 2
        motivi["Peri-implantite"].append("Presenza di impianto")

        # dolore

        if "dolore" in flat_text:
            diagnosi["Peri-implantite"] += 3
            motivi["Peri-implantite"].append("Dolore sull'impianto")

        # sanguinamento

        if "sanguinamento" in flat_text:
            diagnosi["Mucosite peri-implantare"] += 4
            motivi["Mucosite peri-implantare"].append("Sanguinamento peri-implantare")

            diagnosi["Peri-implantite"] += 2
            motivi["Peri-implantite"].append("Sanguinamento peri-implantare")

        # gonfiore

        if "gonfiore" in flat_text:
            diagnosi["Peri-implantite"] += 4
            motivi["Peri-implantite"].append("Gonfiore peri-implantare")

        # pus

        if "pus" in flat_text or "cattivo sapore" in flat_text:
            diagnosi["Peri-implantite"] += 6
            motivi["Peri-implantite"].append("Presenza di pus")

        # mobilità

        if "tutto l'impianto" in flat_text:
            diagnosi["Peri-implantite"] += 8
            motivi["Peri-implantite"].append("Mobilità dell'impianto")
            score += 5
            red_flags.append("Mobilità implantare")

        if "solo la corona" in flat_text:
            diagnosi["Problema protesico"] += 6
            motivi["Problema protesico"].append("Mobilità della sola corona implantare")

        # dolore alla masticazione

        if "masticazione" in flat_text:
            diagnosi["Peri-implantite"] += 2
            motivi["Peri-implantite"].append("Dolore durante la masticazione")

            diagnosi["Problema protesico"] += 2
            motivi["Problema protesico"].append("Dolore durante la masticazione")

        # febbre

        if "febbre" in flat_text:
            diagnosi["Peri-implantite"] += 4
            motivi["Peri-implantite"].append("Febbre associata")
            score += 2

        # antibiotici

        if "antibiotici" in flat_text and "no" in flat_text:
            diagnosi["Peri-implantite"] += 1
            motivi["Peri-implantite"].append("Nessuna terapia antibiotica")

        # recidiva

        if "già avuto problemi" in flat_text:
            diagnosi["Peri-implantite"] += 3
            motivi["Peri-implantite"].append("Problema già presente in passato")

        # impianto recente

        if "meno di 1 mese" in flat_text:
            diagnosi["Complicanza implantare"] += 6
            motivi["Complicanza implantare"].append("Impianto inserito da meno di un mese")

        impianto_recente = any(x in flat_text for x in ["meno di 1 mese", "1-6 mesi"])
        segni_implantari = any(x in flat_text for x in [
            "sanguinamento",
            "dolore",
            "gonfiore",
            "pus",
            "cattivo sapore",
            "mobilità"
        ])

        if impianto_recente and "impianto" in flat_text and segni_implantari:
            diagnosi["Peri-implantite"] += 10
            motivi["Peri-implantite"].append("Impianto recente con segni peri-implantari")

            diagnosi["Mucosite peri-implantare"] += 4
            motivi["Mucosite peri-implantare"].append("Impianto recente con sanguinamento/gonfiore")

            if "meno di 1 mese" in flat_text:
                diagnosi["Complicanza implantare"] += 8
                motivi["Complicanza implantare"].append("Impianto molto recente con sintomi")
    # ==========================
    # PARODONTO
    # ==========================

    if (
            "gengive" in flat_text
            or "gengivale" in flat_text
            or "parodont" in flat_text
            or "sanguinamento" in flat_text
    ):
        if impianto_recente and "impianto" in flat_text and segni_implantari:
            diagnosi["Gengivite"] += 1
            motivi["Gengivite"].append("Sanguinamento peri-implantare")

            diagnosi["Parodontite"] += 1
            motivi["Parodontite"].append("Segni gengivali in presenza di impianto")
        else:

            diagnosi["Gengivite"] += 2
            motivi["Gengivite"].append("Sintomi gengivali")

            diagnosi["Parodontite"] += 2
            motivi["Parodontite"].append("Sintomi gengivali")

        # Sanguinamento

        if "spazzolamento" in flat_text:
            diagnosi["Gengivite"] += 4
            motivi["Gengivite"].append("Sanguinamento durante lo spazzolamento")

        if "spontaneamente" in flat_text:
            diagnosi["Parodontite"] += 4
            motivi["Parodontite"].append("Sanguinamento spontaneo")

        # Gonfiore

        if "gonfie" in flat_text or "arrossate" in flat_text:
            diagnosi["Gengivite"] += 4
            motivi["Gengivite"].append("Gengive gonfie e arrossate")

        # Pus

        if "pus" in flat_text or "cattivo sapore" in flat_text:
            diagnosi["Ascesso parodontale"] += 8
            motivi["Ascesso parodontale"].append("Presenza di pus")

            diagnosi["Parodontite"] += 3
            motivi["Parodontite"].append("Presenza di pus")

        # Alitosi

        if "alito cattivo" in flat_text:
            diagnosi["Parodontite"] += 3
            motivi["Parodontite"].append("Alitosi")

            diagnosi["Gengivite"] += 2
            motivi["Gengivite"].append("Alitosi")

        # Recessioni

        if "ritirate" in flat_text or "più lunghi" in flat_text:
            diagnosi["Parodontite"] += 5
            motivi["Parodontite"].append("Recessioni gengivali")

        # Sensibilità

        if "sensibilità al freddo" in flat_text:
            diagnosi["Parodontite"] += 2
            motivi["Parodontite"].append("Sensibilità al freddo")

            diagnosi["Ipersensibilità dentinale"] += 2
            motivi["Ipersensibilità dentinale"].append("Sensibilità al freddo")

        # Mobilità

        if "uno" in flat_text and "muovono" in flat_text:
            diagnosi["Parodontite"] += 5
            motivi["Parodontite"].append("Mobilità di un dente")

        if "più denti" in flat_text:
            diagnosi["Parodontite"] += 7
            motivi["Parodontite"].append("Mobilità di più denti")
            score += 3

        # Migrazione dentale

        if "spostati" in flat_text:
            diagnosi["Parodontite"] += 5
            motivi["Parodontite"].append("Migrazione dentale")

        # Dolore masticazione

        if "masticazione" in flat_text:
            diagnosi["Parodontite"] += 2
            motivi["Parodontite"].append("Dolore durante la masticazione")

            diagnosi["Ascesso parodontale"] += 2
            motivi["Ascesso parodontale"].append("Dolore durante la masticazione")

        # Fumo

        if "fumatore" in flat_text or "sì" in flat_text:
            diagnosi["Parodontite"] += 2
            motivi["Parodontite"].append("Fumatore")

        # Pregresse cure parodontali

        if "levigatura" in flat_text or "chirurgia gengivale" in flat_text:
            diagnosi["Parodontite"] += 3
            motivi["Parodontite"].append("Pregresse cure parodontali")

        # Peggioramento

        if "peggiorando" in flat_text:
            diagnosi["Parodontite"] += 3
            motivi["Parodontite"].append("Peggioramento progressivo")

        if "rapidamente" in flat_text:
            diagnosi["Ascesso parodontale"] += 3
            motivi["Ascesso parodontale"].append("Peggioramento rapido")

        # Antibiotici

        if "antibiotici" in flat_text:
            diagnosi["Ascesso parodontale"] += 2
            motivi["Ascesso parodontale"].append("Assunzione di antibiotici")


    # ==========================
    # PROTESI
    # ==========================

    if any(x in flat_text for x in [
        "protesi",
        "ponte",
        "dente mancante",
        "scheletrato"
    ]):

        diagnosi["Problema protesico"] += 3
        motivi["Problema protesico"].append("Problema protesico riferito")

        if "si muove" in flat_text:
            diagnosi["Problema protesico"] += 4
            motivi["Problema protesico"].append("Protesi mobile")

        if "protesi mobile" in flat_text:
            diagnosi["Problema protesico"] += 3
            motivi["Problema protesico"].append("Protesi mobile rimovibile")

        if "ponte fisso" in flat_text:
            diagnosi["Problema protesico"] += 2
            motivi["Problema protesico"].append("Problema con ponte fisso")

        if "rotto" in flat_text:
            diagnosi["Problema protesico"] += 4
            motivi["Problema protesico"].append("Protesi o ponte fratturato")

        if "dolore" in flat_text:
            diagnosi["Problema protesico"] += 2
            motivi["Problema protesico"].append("Dolore associato alla protesi")

        if "ferite" in flat_text or "ulcerazioni" in flat_text:
            diagnosi["Lesione della mucosa orale"] += 4
            motivi["Lesione della mucosa orale"].append("Ferite provocate dalla protesi")

        if "masticare" in flat_text:
            diagnosi["Problema protesico"] += 2
            motivi["Problema protesico"].append("Difficoltà nella masticazione")


    # ==========================
    # ESTETICA
    # ==========================

    if any(x in flat_text for x in [
        "sbiancamento",
        "faccette",
        "estetica",
        "sorriso",
        "colore",
        "allineamento"
    ]):

        diagnosi["Richiesta estetica"] += 5
        motivi["Richiesta estetica"].append("Richiesta di miglioramento estetico")

        if "faccette" in flat_text:
            diagnosi["Richiesta estetica"] += 3
            motivi["Richiesta estetica"].append("Richiesta di faccette")

        if "sbiancamento" in flat_text:
            diagnosi["Richiesta estetica"] += 3
            motivi["Richiesta estetica"].append("Richiesta di sbiancamento")

        if "colore" in flat_text:
            diagnosi["Richiesta estetica"] += 2
            motivi["Richiesta estetica"].append("Insoddisfazione per il colore dei denti")

        if "forma" in flat_text:
            diagnosi["Richiesta estetica"] += 2
            motivi["Richiesta estetica"].append("Insoddisfazione per la forma dei denti")

        if "spazi" in flat_text:
            diagnosi["Richiesta estetica"] += 2
            motivi["Richiesta estetica"].append("Presenza di spazi tra i denti")

        if "labbra" in flat_text:
            diagnosi["Richiesta estetica"] += 2
            motivi["Richiesta estetica"].append("Richiesta estetica del sorriso/labbra")

    # ==========================
    # IGIENE
    # ==========================

    if any(x in flat_text for x in [
        "igiene",
        "pulizia",
        "tartaro"
    ]):

        diagnosi["Igiene professionale"] += 5
        motivi["Igiene professionale"].append("Richiesta di igiene professionale")

        if "tartaro" in flat_text:
            diagnosi["Igiene professionale"] += 3
            motivi["Igiene professionale"].append("Presenza di tartaro")

        if "macchie" in flat_text:
            diagnosi["Igiene professionale"] += 2
            motivi["Igiene professionale"].append("Macchie dentali")

        if "alito cattivo" in flat_text:
            diagnosi["Gengivite"] += 2
            motivi["Gengivite"].append("Alitosi")

            diagnosi["Parodontite"] += 2
            motivi["Parodontite"].append("Alitosi")

        if "sanguinano" in flat_text:
            diagnosi["Gengivite"] += 3
            motivi["Gengivite"].append("Sanguinamento gengivale")


    # ==========================
    # CONTROLLO
    # ==========================

    if "controllo" in flat_text:

        diagnosi["Visita di controllo"] += 5
        motivi["Visita di controllo"].append("Richiesta di visita di controllo")

        if "periodico" in flat_text:
            diagnosi["Visita di controllo"] += 2
            motivi["Visita di controllo"].append("Controllo periodico")

        if "primo controllo" in flat_text:
            diagnosi["Visita di controllo"] += 2
            motivi["Visita di controllo"].append("Primo controllo")

        if "nessun sintomo" in flat_text:
            diagnosi["Visita di controllo"] += 2
            motivi["Visita di controllo"].append("Assenza di sintomi")

    # ==========================
    # LESIONI MUCOSA
    # ==========================

    if any(x in flat_text for x in [
        "ulcera",
        "ulcera",
        "ferita",
        "macchia",
        "lesione",
        "afta"
    ]):

        diagnosi["Lesione della mucosa orale"] += 5
        motivi["Lesione della mucosa orale"].append("Presenza di lesione della mucosa")

        if "dolore" in flat_text:
            diagnosi["Lesione della mucosa orale"] += 2
            motivi["Lesione della mucosa orale"].append("Lesione dolorosa")

        if "più di due settimane" in flat_text:
            score += 4
            red_flags.append("Lesione persistente")


    # ==========================
    # ATM
    # ==========================

    if any(x in flat_text for x in [
        "mandibola",
        "atm",
        "click",
        "scatto",
        "articolazione"
    ]):

        diagnosi["Disordine temporo-mandibolare"] += 4
        motivi["Disordine temporo-mandibolare"].append("Sintomi articolari")

        if "apertura" in flat_text:
            diagnosi["Disordine temporo-mandibolare"] += 2
            motivi["Disordine temporo-mandibolare"].append("Limitazione dell'apertura")

        if "click" in flat_text:
            diagnosi["Disordine temporo-mandibolare"] += 3
            motivi["Disordine temporo-mandibolare"].append("Click articolare")

        if "scatto" in flat_text:
            diagnosi["Disordine temporo-mandibolare"] += 3
            motivi["Disordine temporo-mandibolare"].append("Scatto articolare")

        if "dolore" in flat_text:
            diagnosi["Disordine temporo-mandibolare"] += 2
            motivi["Disordine temporo-mandibolare"].append("Dolore articolare")

    # ==========================
    # PRIORITA'
    # ==========================

    if score >= 8:
        priorita = "ALTA"
    elif score >= 4:
        priorita = "MEDIA"
    else:
        priorita = "BASSA"

    # ---------- Red flags sempre ALTA ----------

    if any(flag in red_flags for flag in [
        "Avulsione dentale",
        "Difficoltà respiratoria",
        "Difficoltà alla deglutizione",
        "Trauma cranico associato"
    ]):
        priorita = "ALTA"

    # ---------- Infezioni importanti ----------

    elif "Febbre associata" in red_flags and "gonfiore" in flat_text:
        priorita = "ALTA"

    # ---------- Dolore molto intenso ----------

    elif any(x in flat_text for x in ["10", "9"]):
        if priorita == "BASSA":
            priorita = "MEDIA"

    # ---------- Patologie sempre poco urgenti ----------

    elif ipotesi in [
        "Richiesta estetica",
        "Igiene professionale",
        "Visita di controllo"
    ]:
        priorita = "BASSA"

    # ==========================
    # CLASSIFICA DIAGNOSI
    # ==========================

    diagnosi = dict(
        sorted(
            diagnosi.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )

    # Elimina le diagnosi con punteggio 0
    diagnosi = {
        nome: punti
        for nome, punti in diagnosi.items()
        if punti > 0
    }

    if diagnosi:
        ipotesi = list(diagnosi.keys())[0]
    else:
        ipotesi = "Non determinata"

    diagnosi_differenziali = []

    if diagnosi:

        famiglia_principale = famiglie.get(ipotesi, "")

        for nome in diagnosi.keys():

            if nome == ipotesi:
                continue

            if famiglie.get(nome, "") != famiglia_principale:
                diagnosi_differenziali.append(nome)

            if len(diagnosi_differenziali) == 3:
                break

    # ==========================
    # COMPATIBILITA' CLINICA
    # ==========================

    compatibilita = {}

    for nome, punti in diagnosi.items():

        if punti >= 8:
            compatibilita[nome] = "Alta"

        elif punti >= 4:
            compatibilita[nome] = "Media"

        else:
            compatibilita[nome] = "Bassa"

    # Mantieni solo le diagnosi differenziali presenti
    diagnosi_differenziali = [
        d for d in diagnosi_differenziali
        if d in compatibilita
    ]

    motivi_principali = motivi.get(ipotesi, [])[:5]

    motivi_differenziali = {}

    for d in diagnosi_differenziali:
        motivi_differenziali[d] = motivi.get(d, [])[:3]

    # ==========================
    # REPORT AUTOMATICO
    # ==========================

    report = genera_report(
        priorita,
        ipotesi,
        compatibilita,
        diagnosi_differenziali,
        motivi_principali,
        motivi_differenziali,
        answers,
        red_flags
    )

    return {
        "priorita": priorita,
        "score": score,
        "red_flags": red_flags,
        "ipotesi": ipotesi,
        "compatibilita": compatibilita,
        "diagnosi": diagnosi,
        "diagnosi_differenziali": diagnosi_differenziali,
        "motivi_principali": motivi_principali,
        "motivi_differenziali": motivi_differenziali,
        "report_ai": report
    }