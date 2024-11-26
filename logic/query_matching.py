def query_matching(
    user_input, vector_store, expected_responses, model, similarity_threshold=0.75
):
    """
    Matches user input against a vector store of predefined questions and handles fallbacks.

    Args:
        user_input (str): The user's query or input.
        vector_store (VectorStore): The vector store containing the QA dataset questions.
        expected_responses (dict): A dictionary mapping questions to their expected responses.
        model (ChatOpenAI): The AI model instance for generating reformulated responses.
        similarity_threshold (float): The minimum similarity score to consider a match valid.

    Returns:
        str: A response for the user or a fallback message if no match is found.
    """
    try:
        # Step 1: Perform similarity search
        matches = vector_store.similarity_search_with_score(user_input, k=1)
        if matches:
            match, score = matches[0]
            print(
                f"DEBUG: Match Found: {match.page_content}, Similarity Score: {score}"
            )

            # Step 2: Check if the similarity score meets the threshold
            if score >= similarity_threshold:
                matched_question = match.page_content
                predefined_response = expected_responses.get(
                    matched_question,
                    "I couldn't find a predefined response for this question.",
                )

                # Step 3: Reformulate the response dynamically
                reformulated_response = model.invoke(
                    f"Reformulate the following response to make it more engaging: {predefined_response}"
                )
                return reformulated_response.content.strip()

        # Step 4: If no valid match, provide fallback guidance
        print("DEBUG: No valid match found or low similarity score.")
        return "I'm sorry, I couldn't find a direct answer. Could you provide more details about your request?"

    except Exception as e:
        print(f"Error in query_matching: {e}")
        return "I'm sorry, something went wrong while processing your request."
