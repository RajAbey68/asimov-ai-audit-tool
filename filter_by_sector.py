def modify_query_for_sector_region(query, params, audit_session):
    """Add sector and region filtering to a SQL query"""
    
    # Add sector filtering if specified
    if 'sector_filter' in audit_session and audit_session['sector_filter']:
        query += " AND (sector = ? OR sector IS NULL)"
        params.append(audit_session['sector_filter'])
    
    # Region filtering would require a more complex query with joins
    # For now we'll handle that in the app logic
    
    return query, params