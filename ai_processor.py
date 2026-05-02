import requests


def analyze_email(subject, sender, body):
    """
    Analyse un email et retourne :
    - résumé
    - niveau d'urgence
    - type (travail / perso / spam)
    """

    content = f"""
Subject: {subject}
From: {sender}
Body:
{body}
"""

    prompt = f"""
Tu es un assistant intelligent spécialisé dans l'analyse d'emails.

Analyse cet email et réponds STRICTEMENT avec ce format :

Résumé: (2 phrases max)
Urgence: (faible, moyen, élevé)
Type: (travail, perso, spam)

Email:
{content}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()

        result = response.json().get("response", "")

        return parse_ai_response(result)

    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "summary": "",
            "urgency": "unknown",
            "type": "unknown"
        }


def parse_ai_response(text):
    """
    Transforme la réponse brute du LLM en dict propre
    """

    summary = ""
    urgency = "unknown"
    email_type = "unknown"

    lines = text.split("\n")

    for line in lines:
        lower = line.lower()

        if "résumé" in lower or "resume" in lower:
            summary = line.split(":", 1)[-1].strip()

        elif "urgence" in lower:
            urgency = line.split(":", 1)[-1].strip()

        elif "type" in lower:
            email_type = line.split(":", 1)[-1].strip()

    return {
        "summary": summary,
        "urgency": urgency,
        "type": email_type,
        "raw": text
    }