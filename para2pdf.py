
import logging

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, ListFlowable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 


def generate_pdf_report(data: list[dict], filename: str) -> None:
    """
    Generates a professional-looking PDF for ads.

    Args:
        data (list of dict): A list where each dictionary contains 'StrategyName', 
                             'Headlines' (list), 'Description', and 'Explanation' for a strategy.
        filename (str, optional): The name of the output PDF file. Defaults to "marketing_strategies.pdf".

    """
    logger.info(f"Generating PDF report for {filename}")
    filename = str(filename)
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []


    # Define styles
    styles = getSampleStyleSheet()
    
    # Header Style
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading1'],
                                    fontName= 'Times-Bold', fontSize=16, textColor=colors.black,
                                     alignment=TA_CENTER, spaceAfter=12)
        # Normal text style
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'],
                                    fontName= 'Times-Roman' , fontSize=10, textColor=colors.black,
                                    leading=14)
    
    # Define table styles
    table_header_style = ParagraphStyle('TableHeaderStyle', parent=normal_style, fontName= 'Times-Bold', textColor=colors.whitesmoke, alignment=TA_LEFT)
    table_body_style = normal_style

    # Add Header
    header_text = Paragraph("Marketing Strategies Report", header_style)
    elements.append(header_text)
    elements.append(Spacer(1, 0.25 * inch))

     # Check if data is empty
    if not data:
        no_data_msg = Paragraph("No data available to generate the report.", normal_style)
        elements.append(no_data_msg)
        doc.build(elements)
        print("PDF report generated with no data message.")
        return

    # Prepare table data and header
    table_data = [[Paragraph(cell, table_header_style) for cell in ["Strategy Name", "Headlines", "Description", "Explanation"]]]
    for item in data:
        # Bullet list style for headlines
        bullet_style = ParagraphStyle('BulletList', parent=normal_style, leftIndent=0, bulletIndent=5)
        bullet_list = ListFlowable([Paragraph(headline, bullet_style) for headline in item['Headlines']],
                                   bulletType='bullet', start='circle', bulletFontSize=8)

        table_data.append([
            Paragraph(item['StrategyName'], table_body_style),
            bullet_list,
            Paragraph(item['Description'], table_body_style),
            Paragraph(item['Explanation'], table_body_style)
        ])

    # Define table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
       
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.aliceblue])
    ])

    # Create and style the table
    table = Table(table_data, colWidths=[doc.width / 4.0, doc.width / 3.5, doc.width / 3.5, doc.width / 3.0])
    table.setStyle(table_style)
    elements.append(table)

    # Build the document
    doc.build(elements)
    logger.info(f"PDF report '{filename}' generated successfully!")






