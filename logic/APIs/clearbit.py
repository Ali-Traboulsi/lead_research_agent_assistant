import requests


def enrich_with_clearbit(api_key, csv_data):
    """
    Enriches the lead list with Clearbit's enrichment API.
    """
    enriched_leads = []
    headers = {"Authorization": f"Bearer {api_key}"}

    for lead in csv_data:
        response = requests.get(
            "https://person.clearbit.com/v1/people/find",
            headers=headers,
            params={"email": lead.get("email")},
        )
        if response.status_code == 200:
            result = response.json()
            lead["name"] = result.get("name", {}).get("fullName", "Not Found")
            lead["company"] = result.get("employment", {}).get("name", "Not Found")
            lead["location"] = result.get("geo", {}).get("city", "Not Found")
        else:
            lead["error"] = f"Clearbit API Error: {response.status_code}"
        enriched_leads.append(lead)

    return enriched_leads
