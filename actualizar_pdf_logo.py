import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Función auxiliar para agregar logo a los PDFs
funcion_logo = '''
# Función auxiliar para agregar logo al PDF
def agregar_logo_pdf(elements, config, ticket_width):
    """Agrega logo al PDF si existe en la configuración"""
    if config and config.logo_filename:
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], config.logo_filename)
        if os.path.exists(logo_path):
            try:
                # Calcular tamaño proporcional (max 150px ancho, 60px alto)
                img = RLImage(logo_path)
                aspect = img.imageWidth / img.imageHeight
                if aspect > 2.5:  # Logo muy ancho
                    img_width = min(150, ticket_width - 20)
                    img_height = img_width / aspect
                else:  # Logo normal
                    img_height = 60
                    img_width = img_height * aspect
                
                img.drawWidth = img_width
                img.drawHeight = img_height
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 0.05 * inch))
            except:
                pass  # Si hay error, continuar sin logo
'''

# Buscar después de formato_pesos y antes del primer @app.route
patron = r'(def formato_pesos\(valor\):.*?return.*?\n\n)'
if re.search(patron, content, re.DOTALL):
    content = re.sub(patron, r'\1' + funcion_logo + '\n', content, count=1, flags=re.DOTALL)

# Actualizar api_generar_factura_celular para incluir logo
old_code1 = '''    # Encabezado
    elements.append(Paragraph("<b>CELLSTORE</b>", title_style))'''

new_code1 = '''    # Obtener configuración
    config = ConfiguracionEmpresa.query.first()
    
    # Encabezado con logo
    agregar_logo_pdf(elements, config, ticket_width)
    elements.append(Paragraph(f"<b>{config.nombre if config else 'CELLSTORE'}</b>", title_style))'''

content = content.replace(old_code1, new_code1)

# Hacer lo mismo para la segunda función (generar_factura)
# Buscar la segunda ocurrencia
partes = content.split('# Encabezado\n    elements.append(Paragraph("<b>CELLSTORE</b>", title_style))')
if len(partes) >= 3:
    partes[2] = partes[2].replace(
        'elements.append(Paragraph("<b>CELLSTORE</b>", title_style))',
        '''# Obtener configuración
    config = ConfiguracionEmpresa.query.first()
    
    # Encabezado con logo
    agregar_logo_pdf(elements, config, ticket_width)
    elements.append(Paragraph(f"<b>{config.nombre if config else 'CELLSTORE'}</b>", title_style))''',
        1
    )
    content = '# Encabezado\n    elements.append(Paragraph("<b>CELLSTORE</b>", title_style))'.join(partes)

# También actualizar datos de empresa en los 3 lugares
content = content.replace(
    'elements.append(Paragraph("NIT: 900.123.456-7", subtitle_style))',
    'elements.append(Paragraph(f"NIT: {config.nit if config else \'900.123.456-7\'}", subtitle_style))'
)
content = content.replace(
    'elements.append(Paragraph("Tel: (601) 234-5678", subtitle_style))',
    'elements.append(Paragraph(f"Tel: {config.telefono if config else \'(601) 234-5678\'}", subtitle_style))'
)

# Actualizar función retoma también
old_retoma = '''    # Encabezado
    elements.append(Paragraph("<b>CELLSTORE</b>", title_style))
    elements.append(Paragraph("NIT: 900.123.456-7", subtitle_style))
    elements.append(Paragraph("Tel: (601) 234-5678", subtitle_style))'''

new_retoma = '''    # Obtener configuración
    config = ConfiguracionEmpresa.query.first()
    
    # Encabezado con logo
    agregar_logo_pdf(elements, config, ticket_width)
    elements.append(Paragraph(f"<b>{config.nombre if config else 'CELLSTORE'}</b>", title_style))
    elements.append(Paragraph(f"NIT: {config.nit if config else '900.123.456-7'}", subtitle_style))
    elements.append(Paragraph(f"Tel: {config.telefono if config else '(601) 234-5678'}", subtitle_style))'''

content = content.replace(old_retoma, new_retoma)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Funciones PDF actualizadas para usar logo y configuración')
