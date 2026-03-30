from app import app, db, User

with app.test_client() as client:
    resp = client.post('/login', data={'username': 'sebastian', 'password': 'test123'}, follow_redirects=True)
    html = resp.data.decode('utf-8')
    print(f'After login status: {resp.status_code}')
    
    if 'Iniciar' in html:
        print('Still at login page - wrong password')
    else:
        if 'handleEstadoChange' in html:
            print('handleEstadoChange: FOUND')
        else:
            print('handleEstadoChange: NOT FOUND')
        
        if 'formatearPesos' in html:
            print('formatearPesos: FOUND')
        else:
            print('formatearPesos: NOT FOUND')
        
        count_estado = html.count('cambiar_estado')
        print(f'cambiar_estado forms: {count_estado}')
        
        script_opens = html.count('<script>')
        script_closes = html.count('</script>')
        print(f'Script tags: {script_opens} open, {script_closes} close')
        
        if 'disabled' in html:
            print('Has disabled elements')
        
        # Check for locked buttons
        lock_count = html.count('🔒')
        print(f'Locked buttons (🔒): {lock_count}')
        
        # Find estado buttons area
        import re
        estado_local = html.count("cel.estado == 'local'")
        print(f'Jinja estado checks in rendered output: {estado_local} (should be 0 in rendered)')
        
        vendido_btn = html.count('Vendido</button>')
        retoma_btn = html.count('Retoma</button>')
        print(f'Vendido buttons: {vendido_btn}, Retoma buttons: {retoma_btn}')
