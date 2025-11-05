import sqlite3
import pandas as pd
import json
import os
from datetime import datetime

class DatabaseManager:
    """
    Database management class for the ASIMOV AI Governance Audit Tool.
    Provides methods for querying, analyzing, and exporting data from the audit_controls.db.
    """
    
    def __init__(self, db_file="audit_controls.db"):
        """Initialize the database manager with the specified database file."""
        self.db_file = db_file
        
    def get_connection(self):
        """Create and return a database connection with row factory."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=(), fetch_all=True, commit=False):
        """Execute a SQL query and return the results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            if commit:
                conn.commit()
                return True
            
            if fetch_all:
                results = cursor.fetchall()
            else:
                results = cursor.fetchone()
                
            # Convert to dict for easier serialization
            if results:
                if fetch_all:
                    results = [dict(row) for row in results]
                else:
                    results = dict(results)
                    
            return results
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()
    
    # Framework Analysis Methods
    def get_framework_coverage(self):
        """Get coverage statistics for each framework."""
        query = """
        SELECT 
            framework,
            COUNT(*) as control_count,
            (SELECT COUNT(*) FROM responses WHERE responses.framework = controls.framework) as response_count
        FROM controls
        WHERE framework != ''
        GROUP BY framework
        ORDER BY control_count DESC
        """
        return self.execute_query(query)
    
    def get_category_coverage(self):
        """Get coverage statistics for each category."""
        query = """
        SELECT 
            category,
            COUNT(*) as control_count,
            (SELECT COUNT(*) FROM responses WHERE responses.category = controls.category) as response_count
        FROM controls
        WHERE category != ''
        GROUP BY category
        ORDER BY control_count DESC
        """
        return self.execute_query(query)
    
    def get_risk_distribution(self):
        """Get distribution of controls by risk level."""
        query = """
        SELECT 
            risk_level,
            COUNT(*) as control_count
        FROM controls
        WHERE risk_level != ''
        GROUP BY risk_level
        ORDER BY 
            CASE 
                WHEN risk_level LIKE '%High%' THEN 1
                WHEN risk_level LIKE '%Medium%' THEN 2
                WHEN risk_level LIKE '%Low%' THEN 3
                ELSE 4
            END
        """
        return self.execute_query(query)
    
    # Audit Analysis Methods
    def get_audit_stats(self, session_id):
        """Get comprehensive statistics for a specific audit session."""
        # Overall stats
        overall_query = """
        SELECT 
            COUNT(*) as total_responses,
            AVG(response_score) as avg_score,
            MIN(response_score) as min_score,
            MAX(response_score) as max_score,
            SUM(CASE WHEN response_score >= 3 THEN 1 ELSE 0 END) as compliant_count,
            SUM(CASE WHEN response_score < 3 THEN 1 ELSE 0 END) as non_compliant_count
        FROM responses
        WHERE session_id = ?
        """
        
        # Get audit session details
        session_query = """
        SELECT * FROM audit_sessions WHERE session_id = ?
        """
        
        return {
            "overall": self.execute_query(overall_query, (session_id,), fetch_all=False),
            "session": self.execute_query(session_query, (session_id,), fetch_all=False)
        }
    
    def get_framework_compliance(self, session_id):
        """Get compliance statistics by framework for a specific audit."""
        query = """
        SELECT 
            framework,
            COUNT(*) as control_count,
            AVG(response_score) as avg_score,
            SUM(CASE WHEN response_score >= 3 THEN 1 ELSE 0 END) as compliant_count,
            SUM(CASE WHEN response_score < 3 THEN 1 ELSE 0 END) as non_compliant_count
        FROM responses
        WHERE session_id = ? AND framework != ''
        GROUP BY framework
        ORDER BY avg_score DESC
        """
        return self.execute_query(query, (session_id,))
    
    def get_category_compliance(self, session_id):
        """Get compliance statistics by category for a specific audit."""
        query = """
        SELECT 
            category,
            COUNT(*) as control_count,
            AVG(response_score) as avg_score,
            SUM(CASE WHEN response_score >= 3 THEN 1 ELSE 0 END) as compliant_count,
            SUM(CASE WHEN response_score < 3 THEN 1 ELSE 0 END) as non_compliant_count
        FROM responses
        WHERE session_id = ? AND category != ''
        GROUP BY category
        ORDER BY avg_score DESC
        """
        return self.execute_query(query, (session_id,))
    
    # Export Methods
    def export_to_csv(self, query, params=(), filename=None):
        """Execute a query and export the results to a CSV file."""
        conn = sqlite3.connect(self.db_file)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.csv"
            
        try:
            df = pd.read_sql_query(query, conn, params=params)
            df.to_csv(filename, index=False)
            return filename
        except Exception as e:
            print(f"Export error: {e}")
            return None
        finally:
            conn.close()
    
    def export_to_json(self, query, params=(), filename=None):
        """Execute a query and export the results to a JSON file."""
        conn = sqlite3.connect(self.db_file)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.json"
            
        try:
            df = pd.read_sql_query(query, conn, params=params)
            with open(filename, 'w') as f:
                f.write(df.to_json(orient='records', indent=4))
            return filename
        except Exception as e:
            print(f"Export error: {e}")
            return None
        finally:
            conn.close()
    
    def export_audit_report(self, session_id, format='json'):
        """Generate a comprehensive audit report and export it."""
        # Get audit session details
        session_query = """
        SELECT * FROM audit_sessions WHERE session_id = ?
        """
        session = self.execute_query(session_query, (session_id,), fetch_all=False)
        
        if not session:
            return None
            
        # Get all responses for this session with control details
        responses_query = """
        SELECT 
            r.id, r.control_id, r.response_score, r.reference_text, r.timestamp,
            c.control_name, c.category, c.framework, c.risk_level, c.description
        FROM responses r
        JOIN controls c ON r.control_id = c.id
        WHERE r.session_id = ?
        ORDER BY r.id
        """
        
        # Determine filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_report_{session['session_name'].replace(' ', '_')}_{timestamp}"
        
        if format.lower() == 'csv':
            return self.export_to_csv(responses_query, (session_id,), f"{filename}.csv")
        else:
            return self.export_to_json(responses_query, (session_id,), f"{filename}.json")
    
    # Database Management Methods
    def get_table_info(self, table_name):
        """Get information about a specific table."""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def get_table_count(self, table_name):
        """Get the number of records in a table."""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query, fetch_all=False)
        return result['count'] if result else 0
    
    def get_database_info(self):
        """Get overall information about the database."""
        # Get list of tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = self.execute_query(tables_query)
        
        result = {
            "database_file": self.db_file,
            "file_size_kb": round(os.path.getsize(self.db_file) / 1024, 2),
            "tables": []
        }
        
        # Get info for each table
        for table in tables:
            table_name = table['name']
            result["tables"].append({
                "name": table_name,
                "record_count": self.get_table_count(table_name),
                "columns": self.get_table_info(table_name)
            })
            
        return result
    
    def vacuum_database(self):
        """Optimize the database by vacuuming."""
        conn = sqlite3.connect(self.db_file)
        try:
            conn.execute("VACUUM")
            conn.close()
            return True
        except Exception as e:
            print(f"Vacuum error: {e}")
            return False