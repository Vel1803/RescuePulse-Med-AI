from rapidfuzz import fuzz

# -------- MEDICAL TERMS -------- #
terms = {
    "chest pain": "CRITICAL",
    "breathing": "CRITICAL",
    "stroke": "CRITICAL",
    "accident": "CRITICAL",
    "bleeding": "CRITICAL",
    "blood loss": "CRITICAL",
    "unconscious": "CRITICAL",

    "fever": "MODERATE",
    "infection": "MODERATE",
    "typhoid": "MODERATE",
    "vomiting": "MODERATE",
    "diarrhea": "MODERATE",

    "cold": "LOW",
    "headache": "LOW"
}

# -------- SPELL + MATCH -------- #
def correct_text(text):
    words = text.lower().split()
    corrected = []

    for word in words:
        best_word = word
        best_score = 0

        for term in terms:
            for t_word in term.split():
                score = fuzz.ratio(word, t_word)
                if score > best_score:
                    best_score = score
                    best_word = t_word

        if best_score > 75:
            corrected.append(best_word)
        else:
            corrected.append(word)

    return " ".join(corrected)


def extract_symptoms(text):
    text = correct_text(text)
    found = []

    for term in terms:
        if term in text:
            found.append(term)

    if not found:
        for term in terms:
            score = fuzz.partial_ratio(term, text)
            if score > 75:
                found.append(term)

    return list(set(found))


# -------- MAIN PROCESS -------- #
def process(patient):
    symptoms = extract_symptoms(patient)

    if not symptoms:
        return {
            "input": patient,
            "severity": "LOW",
            "diagnosis": "Needs doctor review",
            "confidence": 0.5
        }

    severity_rank = {"CRITICAL": 3, "MODERATE": 2, "LOW": 1}
    best = "LOW"

    for s in symptoms:
        if severity_rank[terms[s]] > severity_rank[best]:
            best = terms[s]

    if "stroke" in symptoms:
        diagnosis = "Possible stroke"
    elif "chest pain" in symptoms:
        diagnosis = "Possible cardiac issue"
    elif "blood loss" in symptoms or "bleeding" in symptoms:
        diagnosis = "Severe blood loss"
    elif "fever" in symptoms:
        diagnosis = "Possible infection"
    elif "accident" in symptoms:
        diagnosis = "Possible trauma"
    else:
        diagnosis = "Multiple symptoms detected"

    confidence = 0.9 if best == "CRITICAL" else 0.7

    return {
        "input": patient,
        "severity": best,
        "diagnosis": diagnosis,
        "confidence": confidence
    }