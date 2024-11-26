import json


def get_dynamic_prompt(field):
    """
    Generates prompts based on the missing field.
    """
    prompts = {
        "company_size": "What is the size of the companies you're targeting? For example, 50-200 or 500+ employees.",
        "industry": "Which industry are you targeting? For example, Tech or Healthcare.",
        "location": "Where are these companies located? For example, San Francisco or New York.",
        "job_roles": "What roles or job titles are you targeting? For example, CTO or Product Manager.",
    }
    return prompts.get(field, "Please provide more details about your target.")


def update_memory_with_response(value, field, memory_state):
    """
    Updates the memory state with the provided value and removes the field from missing_fields.
    """
    if field in memory_state["missing_fields"]:
        memory_state["extracted_data"][field] = value
        memory_state["missing_fields"].remove(field)


def suggest_next_steps():
    """
    Provides next steps after all required fields are collected.
    """
    return "Next, you can enrich your lead data using LinkedIn or Hunter.io and generate a final lead list."


field_extraction_prompt = """
# Role

You are a Data Extraction Agent.

# Objective

Your objective is to identify and extract specific business details from provided text, including industry, company size, location, and job roles. You should construct a full `user_info` dictionary with these details and indicate if there are any missing fields.

# Context

The extracted information will help provide structured business data from raw text inputs, which will support various business and analytical operations.

# SOP

1. Analyze the user-provided text in the variable user_input.

2. Construct and return the following dictionary:

{ "company_size": null or employee range (e.g., "1-10", "500+"), "industry": null or specific sector (e.g., "Tech", "Healthcare"), "location": null or specific location (e.g., city or country), "job_roles": [] or list of job titles mentioned }

3. In addition to the dictionary, provide a list of fields that are still missing or mention that all fields are complete.

# Examples

**Example 1:**

**Input:**

"Text describing a tech company based in New York with 200+ employees and titles like CEO, Data Scientist, and Product Manager."

**Output:**

{
    "user_info": {
        "company_size": "200+",
        "industry": "Tech",
        "location": "New York",
        "job_roles": ["CEO", "Data Scientist", "Product Manager"]
    },
    "missing_fields": []
}

**Example 2:**

**Input:**

"Description of a healthcare firm in Dubai without specific company size or job titles mentioned."

**Output:**

{
    "user_info": {
        "company_size": null,
        "industry": "Healthcare",
        "location": "Dubai",
        "job_roles": []
    },
    "missing_fields": ["company_size", "job_roles"]
}

**Example 3:**

**Input:**

"A small tech startup with less than 10 employees, located in San Francisco. The team includes a CEO and a CTO."

**Output:**

{
    "user_info": {
        "company_size": "1-10",
        "industry": "Tech",
        "location": "San Francisco",
        "job_roles": ["CEO", "CTO"]
    },
    "missing_fields": []
}
"""


REQUIRED_FIELDS = {"company_size", "industry", "job_roles", "location"}

# Global dictionary to keep track of extracted fields and missing fields
recorded_fields = {
    "user_info": {},
    "missing_fields": list(REQUIRED_FIELDS),  # Initially, all fields are required
}


def extract_user_fields(message, model):
    prompt = (
        field_extraction_prompt
        + f"\nInput: {message}\nResponse format (JSON): {{'company_size': '', 'industry': '', 'job_roles': '', 'location': ''}}"
    )

    try:
        llm_response = model.invoke(prompt)
        llm_extracted_data = json.loads(llm_response)
        print(llm_extracted_data)
        return llm_extracted_data
    except KeyError as e:
        print(f"Missing key in template formatting: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
