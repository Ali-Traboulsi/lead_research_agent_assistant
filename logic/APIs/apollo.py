import requests


def enrich_with_apollo(api_key, csv_data):
    """
    Enriches the lead list with Apollo.io's enrichment API.
    """
    enriched_leads = []
    headers = {"Authorization": f"Bearer {api_key}"}

    for lead in csv_data:
        response = requests.get(
            "https://api.apollo.io/v1/contacts",
            headers=headers,
            params={"email": lead.get("email")},
        )
        if response.status_code == 200:
            result = response.json()
            lead["name"] = result.get("name", "Not Found")
            lead["job_title"] = result.get("job_title", "Not Found")
            lead["company"] = result.get("company", {}).get("name", "Not Found")
        else:
            lead["error"] = f"Apollo API Error: {response.status_code}"
        enriched_leads.append(lead)

    return enriched_leads
