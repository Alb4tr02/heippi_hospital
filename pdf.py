import time
import os
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
def pdf(data):
    route = os.getcwd() + "\\pacient.pdf"
    doc = SimpleDocTemplate(route, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    Story = []
    logotipo = os.getcwd() + "\\logo.png"
    pacient_name = data['usr_name']
    formatoFecha = time.ctime()
    imagen = Image(logotipo, 2 * inch, 1 * inch)
    Story.append(imagen)
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    texto = '%s' % formatoFecha
    Story.append(Paragraph(texto, estilos["Normal"]))
    Story.append(Spacer(1, 12))
    texto = 'Medical history of %s:' % pacient_name
    Story.append(Paragraph(texto, estilos["Normal"]))
    Story.append(Spacer(1, 12))
    dict_list = data['data']
    for dict_p in dict_list:
        texto = 'Hospital: %s' % dict_p['hospital']
        Story.append(Paragraph(texto, estilos["Normal"]))
        Story.append(Spacer(1, 12))
        texto = 'Doctor: %s' % dict_p['doctor']
        Story.append(Paragraph(texto, estilos["Normal"]))
        Story.append(Spacer(1, 12))
        texto = 'Especiality: %s' % dict_p['especiality']
        Story.append(Paragraph(texto, estilos["Normal"]))
        Story.append(Spacer(1, 12))
        texto = 'Observations: %s' % dict_p['details']
        Story.append(Paragraph(texto, estilos["Justify"]))
        Story.append(Spacer(1, 12))
        Story.append(Spacer(1, 12))
        Story.append(Spacer(1, 12))
    texto = 'Heippi developer team.'
    Story.append(Paragraph(texto, estilos["Normal"]))
    doc.build(Story)
    return route