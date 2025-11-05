# Document Reference & Region Management Routes

@app.route('/doc_admin')
def doc_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all reference documents
    cursor.execute('''
        SELECT * FROM reference_documents
        ORDER BY title
    ''')
    documents = cursor.fetchall()
    
    # Get all sectors with region names
    cursor.execute('''
        SELECT s.*, r.name as region_name
        FROM sectors s
        LEFT JOIN regions r ON s.region_id = r.id
        ORDER BY s.name
    ''')
    sectors = cursor.fetchall()
    
    # Get all regions
    cursor.execute('''
        SELECT * FROM regions
        ORDER BY name
    ''')
    regions = cursor.fetchall()
    
    conn.close()
    
    return render_template('doc_admin.html', documents=documents, sectors=sectors, regions=regions)

@app.route('/add_document', methods=['POST'])
def add_document():
    title = request.form.get('title')
    author = request.form.get('author')
    year = request.form.get('year')
    url = request.form.get('url')
    sector = request.form.get('sector')
    description = request.form.get('description')
    
    if not title:
        flash('Document title is required', 'error')
        return redirect(url_for('doc_admin'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO reference_documents (title, author, year, url, sector, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, author, year, url, sector, description))
    
    conn.commit()
    conn.close()
    
    flash('Document added successfully', 'success')
    return redirect(url_for('doc_admin'))

@app.route('/edit_document/<int:doc_id>', methods=['GET', 'POST'])
def edit_document(doc_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')
        url = request.form.get('url')
        sector = request.form.get('sector')
        description = request.form.get('description')
        
        if not title:
            flash('Document title is required', 'error')
            return redirect(url_for('edit_document', doc_id=doc_id))
        
        cursor.execute('''
            UPDATE reference_documents
            SET title = ?, author = ?, year = ?, url = ?, sector = ?, description = ?
            WHERE id = ?
        ''', (title, author, year, url, sector, description, doc_id))
        
        conn.commit()
        flash('Document updated successfully', 'success')
        return redirect(url_for('doc_admin'))
    
    # Get document details
    cursor.execute('SELECT * FROM reference_documents WHERE id = ?', (doc_id,))
    document = cursor.fetchone()
    
    if not document:
        conn.close()
        flash('Document not found', 'error')
        return redirect(url_for('doc_admin'))
    
    # Get all sectors
    cursor.execute('SELECT * FROM sectors ORDER BY name')
    sectors = cursor.fetchall()
    
    conn.close()
    
    return render_template('edit_document.html', document=document, sectors=sectors)

@app.route('/delete_document/<int:doc_id>')
def delete_document(doc_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM reference_documents WHERE id = ?', (doc_id,))
    conn.commit()
    conn.close()
    
    flash('Document deleted successfully', 'success')
    return redirect(url_for('doc_admin'))

@app.route('/add_sector', methods=['POST'])
def add_sector():
    sector_name = request.form.get('sector_name')
    sector_description = request.form.get('sector_description')
    region_id = request.form.get('region_id')
    
    if not sector_name:
        flash('Sector name is required', 'error')
        return redirect(url_for('doc_admin'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO sectors (name, description, region_id, is_standard)
            VALUES (?, ?, ?, 0)
        ''', (sector_name, sector_description, region_id))
        
        conn.commit()
        flash('Sector added successfully', 'success')
    except sqlite3.IntegrityError:
        flash('A sector with that name already exists', 'error')
    
    conn.close()
    return redirect(url_for('doc_admin'))

@app.route('/edit_sector/<int:sector_id>', methods=['GET', 'POST'])
def edit_sector(sector_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        sector_name = request.form.get('sector_name')
        sector_description = request.form.get('sector_description')
        region_id = request.form.get('region_id')
        
        if not sector_name:
            flash('Sector name is required', 'error')
            return redirect(url_for('edit_sector', sector_id=sector_id))
        
        try:
            cursor.execute('''
                UPDATE sectors
                SET name = ?, description = ?, region_id = ?
                WHERE id = ?
            ''', (sector_name, sector_description, region_id, sector_id))
            
            conn.commit()
            flash('Sector updated successfully', 'success')
        except sqlite3.IntegrityError:
            flash('A sector with that name already exists', 'error')
        
        return redirect(url_for('doc_admin'))
    
    # Get sector details
    cursor.execute('SELECT * FROM sectors WHERE id = ?', (sector_id,))
    sector = cursor.fetchone()
    
    if not sector:
        conn.close()
        flash('Sector not found', 'error')
        return redirect(url_for('doc_admin'))
    
    # Get all regions for dropdown
    cursor.execute('SELECT * FROM regions ORDER BY name')
    regions = cursor.fetchall()
    
    conn.close()
    
    return render_template('edit_sector.html', sector=sector, regions=regions)

@app.route('/delete_sector/<int:sector_id>')
def delete_sector(sector_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if it's a standard sector
    cursor.execute('SELECT is_standard FROM sectors WHERE id = ?', (sector_id,))
    result = cursor.fetchone()
    
    if result and result['is_standard'] == 1:
        flash('Standard sectors cannot be deleted', 'error')
    else:
        cursor.execute('DELETE FROM sectors WHERE id = ?', (sector_id,))
        conn.commit()
        flash('Sector deleted successfully', 'success')
    
    conn.close()
    return redirect(url_for('doc_admin'))

@app.route('/add_region', methods=['POST'])
def add_region():
    region_name = request.form.get('region_name')
    region_description = request.form.get('region_description')
    
    if not region_name:
        flash('Region name is required', 'error')
        return redirect(url_for('doc_admin'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO regions (name, description, is_standard)
            VALUES (?, ?, 0)
        ''', (region_name, region_description))
        
        conn.commit()
        flash('Region added successfully', 'success')
    except sqlite3.IntegrityError:
        flash('A region with that name already exists', 'error')
    
    conn.close()
    return redirect(url_for('doc_admin'))

@app.route('/edit_region/<int:region_id>', methods=['GET', 'POST'])
def edit_region(region_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        region_name = request.form.get('region_name')
        region_description = request.form.get('region_description')
        
        if not region_name:
            flash('Region name is required', 'error')
            return redirect(url_for('edit_region', region_id=region_id))
        
        try:
            cursor.execute('''
                UPDATE regions
                SET name = ?, description = ?
                WHERE id = ?
            ''', (region_name, region_description, region_id))
            
            conn.commit()
            flash('Region updated successfully', 'success')
        except sqlite3.IntegrityError:
            flash('A region with that name already exists', 'error')
        
        return redirect(url_for('doc_admin'))
    
    # Get region details
    cursor.execute('SELECT * FROM regions WHERE id = ?', (region_id,))
    region = cursor.fetchone()
    
    if not region:
        conn.close()
        flash('Region not found', 'error')
        return redirect(url_for('doc_admin'))
    
    conn.close()
    
    return render_template('edit_region.html', region=region)

@app.route('/delete_region/<int:region_id>')
def delete_region(region_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if it's a standard region
    cursor.execute('SELECT is_standard FROM regions WHERE id = ?', (region_id,))
    result = cursor.fetchone()
    
    if result and result['is_standard'] == 1:
        flash('Standard regions cannot be deleted', 'error')
    else:
        # Check if any sectors are using this region
        cursor.execute('SELECT COUNT(*) as count FROM sectors WHERE region_id = ?', (region_id,))
        count = cursor.fetchone()['count']
        
        if count > 0:
            flash('This region cannot be deleted because it is in use by one or more sectors', 'error')
        else:
            cursor.execute('DELETE FROM regions WHERE id = ?', (region_id,))
            conn.commit()
            flash('Region deleted successfully', 'success')
    
    conn.close()
    return redirect(url_for('doc_admin'))