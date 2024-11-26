import re
from logic.memory import (
    memory_state,
    update_memory_with_response,
    parse_and_update_memory,
    clean_memory,
)
from logic.prompts import get_dynamic_prompt, suggest_next_steps, extract_user_fields
from logic.query_matching import query_matching
from logic.tracker import progress_state


def clean_agent_response(response):
    """Extracts and formats the model's response content."""
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    return str(response)


def generate_dynamic_guidance(user_input, model):
    prompt = f"""
    User Request: {user_input}
    You are an expert assistant for lead generation. Generate a detailed, step-by-step guide for generating a list of leads, including enrichment and refinement steps.
    """
    response = model.predict(prompt)
    return response


def handle_greetings(user_input):
    """Detect greetings and return an appropriate response."""
    greetings = ["hello", "hi", "hey", "greetings"]
    if user_input.lower() in greetings:
        return "Welcome! Feel free to ask questions or provide details."
    return None


def get_next_field_prompt(memory_state):
    """
    Returns the next prompt for the missing field.
    """
    if memory_state["missing_fields"]:
        next_field = memory_state["missing_fields"][0]
        field_prompts = {
            "company_size": "What is the size of the companies you're targeting?",
            "industry": "What industry are you targeting?",
            "location": "Where are these companies located?",
            "job_roles": "What roles or job titles are you targeting?",
        }
        return field_prompts.get(next_field, "Please provide more details.")
    return "All required information has been collected."


def chat_flow(user_input, model, memory_state, progress_state):
    """
    Handles conversation flow and tracks progress across subsequent phases.
    """
    current_phase = progress_state["current_phase"]

    # Phase 2: Guide user on LinkedIn Sales Navigator
    if current_phase == 2:
        if "linkedin" in user_input.lower():
            return guide_linkedin_sales_navigator(memory_state)
        else:
            return "We are in Phase 2. Would you like guidance on using LinkedIn Sales Navigator?"

    # Phase 3: Accept uploaded data and refine it
    if current_phase == 3:
        if "upload" in user_input.lower():
            return (
                "Please upload your CSV file with leads from LinkedIn Sales Navigator."
            )
        else:
            return "We are in Phase 3. Upload your CSV file to proceed with refinement."

    # Phase 4: Generate final lead list
    if current_phase == 4:
        progress_state["completed_steps"].append("Final lead list generated.")
        progress_state["current_phase"] = None  # No further phases
        return "The final lead list is ready. Download it below."

    # Default fallback
    return "I'm here to assist. Let me know how I can help!"


def chat_entry_point(
    model,
    memory_state,
    vector_store,
    expected_responses,
    user_input,
    progress_state,
):
    """
    Processes a single user input, updates memory, and generates a response.
    Designed for Streamlit workflows (no infinite loop).
    """
    print(f"Type of progress_state: {type(progress_state)}")
    if isinstance(progress_state, dict):
        print(f"Content of progress_state: {progress_state}")
    else:
        print(f"Value of progress_state: {progress_state}")

    try:
        if not isinstance(progress_state, dict):
            # raise TypeError("progress_state is expected to be a dictionary.")
            dict(progress_state)
        if not progress_state.get("conversation_started", False):
            # Your logic here
            pass
    except Exception as e:
        print(f"Error in chat_entry_point: {e}")
        return "I'm sorry, something went wrong while processing your request."

    if not progress_state.get("conversation_started", False):
        progress_state["conversation_started"] = True
        progress_state["current_phase"] = 1
        return handle_greetings(user_input)

    # Start a new conversation if necessary
    if not memory_state.get("conversation_started", False):
        memory_state["conversation_started"] = True
        return "Starting a new conversation. Please provide the company size, industry, location, and job roles."

    if progress_state["current_phase"] == 1:
        # Update memory with user-provided details
        parse_and_update_memory(user_input, memory_state)

        # Check for missing fields
        if memory_state["missing_fields"]:
            return get_next_field_prompt(memory_state)

        # If no fields are missing, suggest next steps
        if not memory_state["missing_fields"]:
            progress_state["completed_steps"].append("Collected required information.")
            progress_state["current_phase"] = 2
            return "All required information has been collected. Moving to Phase 2: Guide on using LinkedIn Sales Navigator."

        if progress_state["current_phase"] == 2:
            if "linkedin" in user_input.lower():
                return guide_linkedin_sales_navigator(memory_state)
            else:
                return "We are in Phase 2. Would you like guidance on using LinkedIn Sales Navigator?"

        # Phase 3: Accepting uploaded data
        if progress_state["current_phase"] == 3:
            if "upload" in user_input.lower():
                return "Please upload your CSV file with leads from LinkedIn Sales Navigator."
            else:
                return "We are in Phase 3. Upload your CSV file to proceed with refinement."

        # Phase 4: Generating the final lead list
        if progress_state["current_phase"] == 4:
            progress_state["completed_steps"].append("Final lead list generated.")
            progress_state["current_phase"] = None  # End conversation
            return "The final lead list is ready. Download it below."

        # Fallback to query
        # matching or dynamic guidance
        response = query_matching(user_input, vector_store, expected_responses, model)
        if response:
            return response

        # Generate dynamic guidance as a last resort
        return generate_dynamic_guidance(user_input, model)


def guide_linkedin_sales_navigator(memory_state):
    """
    Provides step-by-step guidance on using LinkedIn Sales Navigator based on the collected information.
    """
    company_size = memory_state["extracted_data"].get("company_size", "N/A")
    industry = memory_state["extracted_data"].get("industry", "N/A")
    location = memory_state["extracted_data"].get("location", "N/A")
    job_roles = memory_state["extracted_data"].get("job_roles", [])

    # Step-by-step guidance
    guidance = [
        "1. Open LinkedIn Sales Navigator and log in to your account.",
        f"2. Use the filters to narrow your search:",
        f"   - Industry: {industry}",
        f"   - Company size: {company_size}",
        f"   - Location: {location}",
        f"   - Job titles: {', '.join(job_roles) if job_roles else 'N/A'}",
        "3. Export your search results to a CSV file if you have access to Sales Navigator Premium.",
        "4. Ensure the exported file includes columns like Company Name, Contact Name, Email, Job Title, and Location.",
        "5. Once you have the data, upload it here for refinement and lead list generation.",
    ]
    return "\n".join(guidance)
