import pandas as pd


def parse_csv(uploaded_file):
    """
    Parses an uploaded CSV file into a list of dictionaries for processing.

    Args:
        uploaded_file: The uploaded file from Streamlit's file uploader.

    Returns:
        List[dict]: A list of rows represented as dictionaries.
    """
    try:
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(uploaded_file, delimiter=",", encoding="latin1")

        # Convert DataFrame to a list of dictionaries
        data = df.to_dict(orient="records")

        # Validate required fields
        required_fields = {"email", "first_name", "company_domain"}
        missing_fields = required_fields - set(df.columns)
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        return data

    except Exception as e:
        raise ValueError(f"Error processing the CSV file: {e}")
