import sqlite3
import pandas as pd

def create_database(db_file):
    """
    Create a SQLite database with the controls table schema.
    
    Args:
        db_file (str): Path to the SQLite database file
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Drop the table if it exists
        cursor.execute("DROP TABLE IF EXISTS controls")
        
        # Create the controls table with the specified schema
        cursor.execute('''
            CREATE TABLE controls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                control_name TEXT,
                category TEXT,
                framework TEXT,
                explainability TEXT,
                description TEXT,
                evidence TEXT,
                risk_level TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    except sqlite3.Error as e:
        raise Exception(f"Database creation error: {e}")

def insert_data_to_db(db_file, df):
    """
    Insert data from a pandas DataFrame into the controls table.
    
    Args:
        db_file (str): Path to the SQLite database file
        df (pandas.DataFrame): DataFrame containing the control data
        
    Returns:
        int: Number of records inserted
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Filter dataframe to only include columns that exist in our table
        table_columns = [
            'control_name', 'category', 'framework', 'explainability',
            'description', 'evidence', 'risk_level'
        ]
        
        # Get the intersection of dataframe columns and table columns
        cols_to_use = [col for col in df.columns if col.lower() in table_columns]
        
        # Create a mapping of dataframe column names to table column names
        col_mapping = {col: col.lower() for col in cols_to_use}
        
        # Rename columns to match the table schema
        df_for_db = df[cols_to_use].rename(columns=col_mapping)
        
        # Make sure all required columns exist
        for col in table_columns:
            if col not in df_for_db.columns:
                df_for_db[col] = ""
        
        # Insert data row by row
        count = 0
        for _, row in df_for_db.iterrows():
            cursor.execute('''
                INSERT INTO controls (
                    control_name, category, framework, explainability, 
                    description, evidence, risk_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['control_name'], 
                row['category'],
                row['framework'], 
                row['explainability'],
                row['description'], 
                row['evidence'],
                row['risk_level']
            ))
            count += 1
        
        conn.commit()
        conn.close()
        
        return count
        
    except sqlite3.Error as e:
        raise Exception(f"Database insertion error: {e}")

def query_db(db_file, query):
    """
    Execute a query on the SQLite database.
    
    Args:
        db_file (str): Path to the SQLite database file
        query (str): SQL query to execute
        
    Returns:
        list: Result of the query
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        conn.close()
        
        return result
        
    except sqlite3.Error as e:
        raise Exception(f"Database query error: {e}")
