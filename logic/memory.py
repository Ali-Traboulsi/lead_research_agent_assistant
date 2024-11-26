import re


memory_state = {
    "conversation_started": False,
    "missing_fields": ["company_size", "industry", "location", "job_roles"],
    "extracted_data": {},
}


def update_memory_with_response(user_input, field):
    """
    Updates memory state with user-provided information.
    """
    if field in memory_state["missing_fields"]:
        memory_state["extracted_data"][field] = user_input
        memory_state["missing_fields"].remove(field)
        return user_input
    return None


def clean_memory():
    """
    Resets memory for a new session.
    """
    global memory_state
    memory_state = {
        "conversation_started": False,
        "missing_fields": ["company_size", "industry", "location", "job_roles"],
        "extracted_data": {},
    }


def generate_contextual_response(memory_state, model):
    """
    Generates a context-aware response based on the current memory state.
    """
    missing_fields = memory_state["missing_fields"]

    # Craft the dynamic prompt based on missing fields
    if missing_fields:
        prompt = f"""
        You are an assistant helping with lead generation. The user asked, "Which details are needed?".
        Based on the current context, the following details are missing: {', '.join(missing_fields)}.
        Generate a helpful and engaging response to guide the user in providing these details.
        """
        response = model.invoke(prompt)
        return response.strip()

    # If no fields are missing
    return "All required details have already been collected!"


def parse_and_update_memory(user_input, memory_state):
    """
    Parses user input for multiple fields and updates the memory state.
    """
    field_patterns = {
        "company_size": r"(company size|size):\s*(.+)",
        "industry": r"(industry|sector):\s*(.+)",
        "location": r"(location):\s*(.+)",
        "job_roles": r"(job roles|roles):\s*(.+)",
    }

    for field, pattern in field_patterns.items():
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            value = match.group(2).strip()
            memory_state["extracted_data"][field] = value
            if field in memory_state["missing_fields"]:
                memory_state["missing_fields"].remove(field)
