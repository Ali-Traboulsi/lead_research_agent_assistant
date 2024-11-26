import pandas as pd
import random


# Generate sample data
def generate_sample_leads(num_leads=10):
    first_names = ["John", "Jane", "Alex", "Emily", "Michael", "Sarah", "Chris", "Anna"]
    last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Davis"]
    company_names = [
        "TechCorp",
        "HealthPlus",
        "EcoEnergy",
        "DataDynamics",
        "Innovatech",
    ]
    domains = [
        "techcorp.com",
        "healthplus.com",
        "ecoenergy.com",
        "datadynamics.com",
        "innovatech.com",
    ]

    leads = []
    for i in range(num_leads):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        company_name = random.choice(company_names)
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
        leads.append(
            {
                "id": i + 1,
                "first_name": first_name,
                "last_name": last_name,
                "company_domain": company_name,
                "email": email,
            }
        )

    return pd.DataFrame(leads)


# Generate and save to CSV
sample_leads = generate_sample_leads(10)
sample_leads.to_csv("sample_leads.csv", index=False)
print(sample_leads)
