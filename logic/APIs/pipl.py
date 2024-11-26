import requests


def enrich_with_pipl(api_key, csv_data):
    """
    Enriches the lead list with Pipl's search API.
    """
    enriched_leads = []
    for lead in csv_data:
        response = requests.get(
            "https://api.pipl.com/search/",
            params={"key": api_key, "email": lead.get("email")},
        )
        if response.status_code == 200:
            result = response.json()
            lead["phone"] = result.get("phone", {}).get("number", "Not Found")
            lead["job_title"] = result.get("jobs", [{}])[0].get("title", "Not Found")
            lead["social_profiles"] = [
                profile.get("url") for profile in result.get("socialProfiles", [])
            ]
        else:
            lead["error"] = f"Pipl API Error: {response.status_code}"
        enriched_leads.append(lead)

    return enriched_leads
