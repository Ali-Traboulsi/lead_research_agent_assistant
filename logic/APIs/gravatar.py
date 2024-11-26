import hashlib
import requests


def enrich_with_gravatar(csv_data):
    """
    Enriches the lead list with Gravatar's publicly available data.
    """
    enriched_leads = []
    for lead in csv_data:
        email_hash = hashlib.md5(lead["email"].strip().lower().encode()).hexdigest()
        gravatar_url = f"https://api.gravatar.com/v3/{email_hash}.json"
        response = requests.get(
            gravatar_url,
            params={
                "GRAVATAR": "1670:gk-El30VSmSA7Ouf-Av9VRqkR5bvd4HMgwhBonNfi7kGlL1Kt6839tUscm60kILJ"
            },
        )
        if response.status_code == 200:
            result = response.json()
            lead["profile"] = result.get("entry", [{}])[0].get(
                "profileUrl", "Not Found"
            )
        else:
            lead["profile"] = "Gravatar data not available"
        enriched_leads.append(lead)
    return enriched_leads
