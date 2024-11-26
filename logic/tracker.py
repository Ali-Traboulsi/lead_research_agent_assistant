progress_state = {
    "current_phase": 1,
    "phases": {
        1: "Collect required information.",
        2: "Guide the user to use LinkedIn Sales Navigator.",
        3: "Accept uploaded data and refine it.",
        4: "Generate the final lead list.",
    },
    "completed_steps": [],
    "current_step_details": None,
}

# Define expected responses
expected_responses = {
    "What is your target industry?": "The target industry defines the sector you're aiming for, such as Tech or Healthcare.",
    "What roles are you targeting?": "Roles like CTO, Product Manager, and Data Scientist are common targets.",
    "Where are these companies located?": "Specify locations such as 'San Francisco' or 'New York.'",
    "What is the size of the companies you're targeting?": "Company size helps narrow down your target, such as",
}


def handle_phase_query(user_input, progress_state, model):
    """
    Responds to user queries about the current phase and progress dynamically using the model.
    """
    current_phase = progress_state["current_phase"]

    # Prompt the model to interpret user input in the context of the current phase
    prompt = f"""
    User Query: "{user_input}"
    Progress Tracker:
    - Current Phase: {current_phase} - {progress_state['phases'][current_phase]}
    - Completed Steps: {', '.join(progress_state['completed_steps']) if progress_state['completed_steps'] else 'None'}

    As an intelligent assistant, interpret the user's intent based on the query and provide a helpful response relevant to the current phase. Be concise and direct. Use the progress tracker to guide the response.
    """

    response = model.invoke(prompt)

    # Fallback to default response if the model fails to generate a useful output
    if not response or "I'm not sure" in response:
        response = f"We are in Phase {current_phase}: {progress_state['phases'][current_phase]}."

    return response.strip()
