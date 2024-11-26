import streamlit as st
import hashlib

from logic.APIs.apollo import enrich_with_apollo
from logic.APIs.clearbit import enrich_with_clearbit
from logic.APIs.gravatar import enrich_with_gravatar
from logic.APIs.hunter import enrich_with_hunter
from logic.APIs.pipl import enrich_with_pipl
from logic.helpers.parse_csv import parse_csv
from logic.memory import clean_memory, generate_contextual_response, memory_state
from langchain_cohere import ChatCohere
import os
from dotenv import load_dotenv

from logic.tracker import progress_state, expected_responses

# Load the QA dataset
load_dotenv()

model = ChatCohere(
    cohere_api_key=os.getenv("COHERE_API_KEY"),
)

# Initialize UI
st.title("AI Lead Generation Assistant")
st.sidebar.title("Conversation Settings")

# Button to start a new session
if st.sidebar.button("Start New Session"):
    clean_memory()
    st.session_state["conversation_history"] = []
    st.session_state["conversation_started"] = False

import streamlit as st

# Initialize session state variables
if "conversation_started" not in st.session_state:
    st.session_state["conversation_started"] = False
if "current_phase" not in st.session_state:
    st.session_state["current_phase"] = 1
if "completed_steps" not in st.session_state:
    st.session_state["completed_steps"] = []
if "user_input" not in st.session_state:
    st.session_state["user_input"] = None

# Define phase descriptions
phase_descriptions = {
    1: "Collect required information.",
    2: "Guide the user to use LinkedIn Sales Navigator.",
    3: "Accept uploaded data and refine it.",
    4: "Generate the final lead list.",
}

# Sidebar Progress Tracker
st.sidebar.title("Progress Tracker")
st.sidebar.write(
    f"Current Phase: {st.session_state['current_phase']} - {phase_descriptions[st.session_state['current_phase']]}"
)
if st.session_state["completed_steps"]:
    st.sidebar.write("Completed Steps:")
    for step in st.session_state["completed_steps"]:
        st.sidebar.write(f"- {step}")

# Main logic based on the current phase
if st.session_state["current_phase"] == 1:
    st.write("### Phase 1: Collect Required Information")
    company_size = st.text_input("Company Size (e.g., 100-500 employees)")
    industry = st.text_input("Industry (e.g., Tech, Healthcare)")
    location = st.text_input("Location (e.g., San Francisco, New York)")
    job_roles = st.text_input("Job Roles (e.g., CTO, Product Manager)")

    if st.button("Submit Details"):
        # Store user input in session state
        st.session_state["user_input"] = {
            "company_size": company_size,
            "industry": industry,
            "location": location,
            "job_roles": job_roles,
        }

        # Ensure all fields are filled
        if all(st.session_state["user_input"].values()):
            st.session_state["completed_steps"].append(
                "Collected required information."
            )
            st.session_state["current_phase"] += 1
            st.success("Details collected successfully! Click 'Next Step' to proceed.")
        else:
            st.error("Please fill in all fields before proceeding.")

elif st.session_state["current_phase"] == 2:
    st.write("### Phase 2: Guide on LinkedIn Sales Navigator")
    if st.button("Get Guidance"):
        st.write("1. Open LinkedIn Sales Navigator and log in to your account.")
        st.write("2. Use filters to narrow your search:")
        st.write(f"   - Industry: {st.session_state['user_input']['industry']}")
        st.write(f"   - Company size: {st.session_state['user_input']['company_size']}")
        st.write(f"   - Location: {st.session_state['user_input']['location']}")
        st.write(f"   - Job titles: {st.session_state['user_input']['job_roles']}")
        st.write("3. Export the data as a CSV file for upload.")

    if st.button("Next Step"):
        st.session_state["completed_steps"].append(
            "Guided on using LinkedIn Sales Navigator."
        )
        st.session_state["current_phase"] += 1
        st.success("Click 'Next Step' to proceed to data upload.")


elif st.session_state["current_phase"] == 3:
    st.write("### Phase 3: Enrich and Refine Data")

    # File Upload Section
    uploaded_file = st.file_uploader("Upload your CSV file with leads:")
    if uploaded_file is not None:
        try:
            csv_data = parse_csv(uploaded_file)
            st.write("CSV file successfully parsed!")
            st.write(csv_data)  # Display parsed data for review

            # API Selection
            api_choice = st.selectbox(
                "Choose an API for enrichment:",
                ["Hunter.io", "Clearbit", "Pipl", "Apollo", "FullContact", "Gravatar"],
            )

            # Start Enrichment
            if st.button("Start Enrichment"):
                if api_choice == "Hunter.io":
                    enriched_data = enrich_with_hunter(
                        api_key="1adbfdb09c47a88f4b354e9d87575612896844ad",
                        csv_data=csv_data,
                    )
                elif api_choice == "Apollo":
                    enriched_data = enrich_with_apollo(
                        api_key="i-USRUbzLd4x93uFuEKQEQ", csv_data=csv_data
                    )
                elif api_choice == "Gravatar":
                    enriched_data = enrich_with_gravatar(csv_data=csv_data)

                st.write("Data enrichment complete!")
                st.write(enriched_data)  # Display enriched data

            if st.button("Next Step"):
                st.session_state["completed_steps"].append("Data uploaded and refined.")
                st.session_state["current_phase"] += 1
                st.success("Data refined successfully! Moving to Phase 4.")

        except ValueError as e:
            st.error(str(e))

elif st.session_state["current_phase"] == 4:
    st.write("### Phase 4: Generate Lead List")
    st.write("The final lead list is ready. Click below to download.")

    # Use the refined data from Phase 3
    refined_data = st.session_state.get("refined_data", "No data available.")
    st.download_button(
        label="Download Lead List",
        data=refined_data,  # Replace with actual refined data
        file_name="curated_lead_list.csv",
        mime="text/csv",
    )
    if st.button("Restart Process"):
        # Reset session state for a new session
        st.session_state["completed_steps"] = []
        st.session_state["current_phase"] = 1
        st.session_state["conversation_started"] = False
        st.session_state["user_input"] = {}
        st.success("Restarting the process.")
