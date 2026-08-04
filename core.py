import json

with open("flow.json", "r", encoding="utf-8") as f:
    FLOW = json.load(f)

# =========================
# VALIDAZIONE FLOW
# =========================

for node, data in FLOW.items():
    nxt = data.get("next")

    if nxt and nxt != "completed" and nxt not in FLOW:
        raise Exception(
            f"Errore nel flow.json: il nodo '{node}' punta a '{nxt}' che non esiste."
        )


def next_node(node, answer):
    if isinstance(answer, list):
        answer = " ".join(answer).strip().lower()
    else:
        answer = str(answer).strip().lower()

    # ROOT: scelta iniziale
    if node == "root":
        mapping = {
            "dolore": "pain_1",
            "gonfiore": "sw_1",
            "trauma": "tr_1",
            "dente rotto": "broken_1",
            "otturazione o corona saltata": "rest_1",
            "sanguinamento gengivale": "paro_1",
            "gengive o denti mobili": "paro_1",
            "problema con impianto": "imp_1",
            "problema con apparecchio ortodontico": "ortho_1",
            "dente mancante / protesi": "prost_1",
            "estetica": "est_1",
            "pulizia dei denti": "clean_1",
            "controllo": "check_1",
            "altro": "other_1",
        }

        return mapping.get(answer, "med_1")

    # FLUSSO GENERICO DAL JSON
    if node in FLOW:
        base = FLOW[node].get("next")

        if not base:
            return "completed"

        if base not in FLOW and base != "completed":
            return "med_1"

        return base

    # FALLBACK ASSOLUTO
    return "med_1"