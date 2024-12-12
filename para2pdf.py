from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, ListFlowable, ListItem, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
import requests
from io import BytesIO
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logeer = logging.getLogger(__name__)


# Constants for default fonts
DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_BOLD = "Helvetica-Bold"

# Fallback for fonts
if DEFAULT_FONT not in pdfmetrics.getRegisteredFontNames():
    DEFAULT_FONT = "Times-Roman"
if DEFAULT_FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
    DEFAULT_FONT_BOLD = "Times-Bold" if "Times-Bold" in pdfmetrics.getRegisteredFontNames() else DEFAULT_FONT

# Style definitions
def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=12,
            fontName=DEFAULT_FONT_BOLD,
        ),
        "heading": ParagraphStyle(
            "HeadingStyle",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.black,
            spaceBefore=12,
            spaceAfter=6,
            fontName=DEFAULT_FONT_BOLD,
        ),
        "subheading": ParagraphStyle(
            "SubheadingStyle",
            parent=styles["Heading3"],
            fontSize=12,
            textColor=colors.black,
            spaceBefore=6,
            spaceAfter=6,
            fontName=DEFAULT_FONT_BOLD,
        ),
        "body": ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            fontName=DEFAULT_FONT,
        ),
    }

# Image handling
def fetch_image(image_url: str, fallback_text: str, style: ParagraphStyle) -> List[Any]:
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        img_data = BytesIO(response.content)
        return [Image(img_data, width=4 * inch, height=3 * inch, hAlign='CENTER'), Spacer(1, 12)]
    except Exception as e:
        return [Paragraph(fallback_text, style), Spacer(1, 12)]

# Generate ingredient section
def generate_ingredient_section(ingredients: Dict[str, List[str]], styles: Dict[str, ParagraphStyle]) -> List[Any]:
    elements = [Paragraph("Ingredients", styles["heading"])]
    for category, items in ingredients.items():
        elements.append(Paragraph(category, styles["subheading"]))
        elements.append(ListFlowable(
            [ListItem(Paragraph(item, styles["body"]), bulletType='bullet', leftIndent=10) for item in items],
            bulletType='bullet',
        ))
        elements.append(Spacer(1, 6))
    return elements

# Generate table
def generate_table(data: List[List[Any]], col_widths: List[float], styles: TableStyle) -> Table:
    table = Table(data, colWidths=col_widths)
    table.setStyle(styles)
    return table

# Main function to create the PDF
def create_recipe_pdf(recipe_data: Dict[str, Any], filename: str = "recipe.pdf"):

    """
    Generates a recipe PDF using the provided recipe data.
    
    Args:
        recipe_data (dict): A dictionary containing the recipe information.
        filename (str): path to save the pdf

    """
    logging.info(f"Generating PDF for recipe: {recipe_data['title']}")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = get_styles()
    elements = []

    # Title
    elements.append(Paragraph(recipe_data['title'], styles["title"]))

    # Image
    elements.extend(fetch_image(
        recipe_data.get('image', ""),
        "Image Not Available",
        styles["body"]
    ))

    # Ingredients
    elements.extend(generate_ingredient_section(recipe_data['ingredients'], styles))

    # Instructions
    elements.append(PageBreak())
    elements.append(Paragraph("Instructions", styles["heading"]))
    elements.append(ListFlowable(
        [ListItem(Paragraph(item, styles["body"]), bulletType='1', leftIndent=10) for item in recipe_data['instructions']],
        bulletType='1',
    ))

    # Cooking Notes
    if recipe_data.get('cooking_notes'):
        elements.append(Paragraph("Cooking Notes", styles["heading"]))
        elements.append(ListFlowable(
            [ListItem(Paragraph(item, styles["body"]), bulletType='bullet', leftIndent=10) for item in recipe_data['cooking_notes']],
            bulletType='bullet',
        ))

    # Diet Information
    if 'diet' in recipe_data:
        elements.append(PageBreak())
        elements.append(Paragraph("Diet", styles["heading"]))
        diet_data = [[Paragraph(key, styles["body"]), Paragraph(str(value), styles["body"])]
                     for section in recipe_data['diet'].values() for key, value in section.items()]
        elements.append(generate_table(
            [['Category', 'Value']] + diet_data,
            col_widths=[1.5 * inch, 3 * inch],
            styles=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), DEFAULT_FONT),
            ])
        ))

    # Nutritional Information
    elements.append(PageBreak())
    elements.append(Paragraph("Nutritional Information (per serving)", styles["heading"]))
    nutrients = [['Nutrient', 'Amount', 'Percent of Daily Needs']] + [
        [n['name'], f"{n['amount']:.2f} {n['unit']}", f"{n['percentOfDailyNeeds']:.2f}%"] for n in recipe_data['nutrients']
    ]
    elements.append(generate_table(
        nutrients,
        col_widths=[2.5 * inch, 2 * inch, 2 * inch],
        styles=TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ])
    ))

    # Build PDF
    doc.build(elements)
    logging.info(f"PDF generated: {filename}")
