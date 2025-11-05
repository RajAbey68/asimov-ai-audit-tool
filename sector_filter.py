"""
Helper functions for sector and region filtering in ASIMOV Audit Tool
"""

def apply_sector_filter_to_query(query, params, audit_session):
    """
    Add sector filtering to a database query
    
    Args:
        query (str): The base SQL query
        params (list): Query parameters
        audit_session (dict): Audit session information
        
    Returns:
        tuple: Updated query string and parameters
    """
    # Apply sector filter if it exists
    if 'sector_filter' in audit_session and audit_session['sector_filter']:
        # Include controls that match the sector or have no sector specified
        query += " AND (sector = ? OR sector IS NULL)"
        params.append(audit_session['sector_filter'])
        
    return query, params


def get_region_specific_controls(controls, region_name):
    """
    Filter controls based on region relevance
    
    Args:
        controls (list): List of controls
        region_name (str): Region name to filter by
        
    Returns:
        list: Filtered list of controls relevant to the region
    """
    if not region_name or region_name == "Global":
        # Global region includes all controls
        return controls
        
    # This would be based on a more complex region-control mapping
    # For now we'll return all controls since our database doesn't yet
    # have detailed region-specific information for each control
    return controls


def enrich_control_with_region_context(control, region_name):
    """
    Add region-specific information to a control
    
    Args:
        control (dict): Control information
        region_name (str): Region name
        
    Returns:
        dict: Control with added region information
    """
    # Clone the control to avoid modifying the original
    enriched_control = dict(control)
    
    # Add region information
    if region_name:
        enriched_control['region'] = region_name
        
    return enriched_control