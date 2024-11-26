import requests


def enrich_with_hunter(api_key, csv_data):
    """
    Enriches the lead list with emails using Hunter.io API.
    """
    enriched_leads = []
    for lead in csv_data:
        response = requests.get(
            f"https://api.hunter.io/v2/email-finder",
            params={
                "domain": lead["company_domain"],
                "first_name": lead["first_name"],
                "last_name": lead["last_name"],
                "api_key": api_key,
            },
        )
        if response.status_code == 200:
            result = response.json()
            lead["email"] = result.get("data", {}).get("email", "Not Found")
            enriched_leads.append(lead)
        else:
            lead["email"] = "Error in enrichment"
            enriched_leads.append(lead)
    return enriched_leads
