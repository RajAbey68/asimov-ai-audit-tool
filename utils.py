import pandas as pd
import re

def sanitize_dataframe(df):
    """
    Sanitize a pandas DataFrame by:
    1. Converting column names to snake_case
    2. Handling missing values
    3. Removing leading/trailing whitespaces
    
    Args:
        df (pandas.DataFrame): Input DataFrame
        
    Returns:
        pandas.DataFrame: Sanitized DataFrame
    """
    # Make a copy of the DataFrame to avoid modifying the original
    df_clean = df.copy()
    
    # Convert column names to snake_case
    df_clean.columns = [snake_case(col) for col in df_clean.columns]
    
    # Replace NaN values with empty strings
    df_clean = df_clean.fillna("")
    
    # Strip leading/trailing whitespaces from string columns
    for col in df_clean.columns:
        if pd.api.types.is_object_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].astype(str).str.strip()
    
    return df_clean

def snake_case(s):
    """
    Convert a string to snake_case.
    
    Args:
        s (str): Input string
        
    Returns:
        str: String converted to snake_case
    """
    # Replace spaces and other separators with underscore
    s = re.sub(r'[\s\-]+', '_', s)
    # Remove any non-alphanumeric characters (except underscores)
    s = re.sub(r'[^\w\s]', '', s)
    # Convert to lowercase
    return s.lower()

def map_column_names(df):
    """
    Map common column name variations to standard names.
    This helps with handling different naming conventions in the input file.
    
    Args:
        df (pandas.DataFrame): Input DataFrame
        
    Returns:
        pandas.DataFrame: DataFrame with standardized column names
    """
    column_mapping = {
        # Map AI Toolkit specific columns to our standard names
        'control_name': 'control_name',
        'control_number': 'control_name',  # Use control number as part of name if needed
        
        'control_category': 'category',
        'control_family': 'category',
        
        'eu_ai_law': 'framework',
        'nist_800-53_rev_5\n': 'framework',
        'secure_controls_framework_(scf)\n': 'framework',
        
        # For explainability, we'll use a combination of explanation dimensions
        'rationale_explanation_description': 'explainability',
        
        'ai-specific_description_of_the_control': 'description',
        
        'data_explanation_evidence/deliverables/artifacts': 'evidence',
        'fairness_explanation_evidence/deliverables/artifacts': 'evidence',
        'rationale_explanation_evidence/deliverables/artifacts': 'evidence',
        
        'high-risk_control?': 'risk_level',
    }
    
    # Create a new mapping for the actual columns in the dataframe
    actual_mapping = {}
    for col in df.columns:
        col_lower = col.lower().replace(' ', '_')  # Convert spaces to underscores for comparison
        if col_lower in column_mapping:
            actual_mapping[col] = column_mapping[col_lower]
    
    # Apply the mapping
    return df.rename(columns=actual_mapping)
