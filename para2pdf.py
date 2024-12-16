# from reportlab.lib.pagesizes import letter
# from reportlab.lib import colors
# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, ListFlowable, ListItem, PageBreak
# )
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.pdfbase import pdfmetrics
# import requests
# from io import BytesIO
# from typing import Dict, Any, Optional, List
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logeer = logging.getLogger(__name__)


# # Constants for default fonts
# DEFAULT_FONT = "Helvetica"
# DEFAULT_FONT_BOLD = "Helvetica-Bold"

# # Fallback for fonts
# if DEFAULT_FONT not in pdfmetrics.getRegisteredFontNames():
#     DEFAULT_FONT = "Times-Roman"
# if DEFAULT_FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
#     DEFAULT_FONT_BOLD = "Times-Bold" if "Times-Bold" in pdfmetrics.getRegisteredFontNames() else DEFAULT_FONT

# # Style definitions
# def get_styles():
#     styles = getSampleStyleSheet()
#     return {
#         "title": ParagraphStyle(
#             "TitleStyle",
#             parent=styles["Title"],
#             fontSize=24,
#             textColor=colors.darkblue,
#             spaceAfter=12,
#             fontName=DEFAULT_FONT_BOLD,
#         ),
#         "heading": ParagraphStyle(
#             "HeadingStyle",
#             parent=styles["Heading2"],
#             fontSize=14,
#             textColor=colors.black,
#             spaceBefore=12,
#             spaceAfter=6,
#             fontName=DEFAULT_FONT_BOLD,
#         ),
#         "subheading": ParagraphStyle(
#             "SubheadingStyle",
#             parent=styles["Heading3"],
#             fontSize=12,
#             textColor=colors.black,
#             spaceBefore=6,
#             spaceAfter=6,
#             fontName=DEFAULT_FONT_BOLD,
#         ),
#         "body": ParagraphStyle(
#             "BodyStyle",
#             parent=styles["Normal"],
#             fontSize=10,
#             textColor=colors.black,
#             spaceAfter=6,
#             fontName=DEFAULT_FONT,
#         ),
#     }

# # Generate ingredient section
# def generate_ingredient_section(ingredients: Dict[str, List[str]], styles: Dict[str, ParagraphStyle]) -> List[Any]:
#     elements = [Paragraph("Ingredients", styles["heading"])]
#     for category, items in ingredients.items():
#         elements.append(Paragraph(category, styles["subheading"]))
#         elements.append(ListFlowable(
#             [ListItem(Paragraph(item, styles["body"]), bulletType='bullet', leftIndent=10) for item in items],
#             bulletType='bullet',
#         ))
#         elements.append(Spacer(1, 6))
#     return elements

# # Generate table
# def generate_table(data: List[List[Any]], col_widths: List[float], styles: TableStyle) -> Table:
#     table = Table(data, colWidths=col_widths)
#     table.setStyle(styles)
#     return table

# # Main function to create the PDF
# def create_recipe_pdf(recipe_data: Dict[str, Any], filename: str = "recipe.pdf"):

#     """
#     Generates a recipe PDF using the provided recipe data.
    
#     Args:
#         recipe_data (dict): A dictionary containing the recipe information.
#         filename (str): path to save the pdf

#     """
#     logging.info(f"Generating PDF for recipe: {recipe_data['title']}")
#     doc = SimpleDocTemplate(filename, pagesize=letter)
#     styles = get_styles()
#     elements = []

#     # Title
#     elements.append(Paragraph(recipe_data['title'], styles["title"]))

#     # Ingredients
#     elements.extend(generate_ingredient_section(recipe_data['ingredients'], styles))

#     # Instructions
#     elements.append(PageBreak())
#     elements.append(Paragraph("Instructions", styles["heading"]))
#     elements.append(ListFlowable(
#         [ListItem(Paragraph(item, styles["body"]), bulletType='1', leftIndent=10) for item in recipe_data['instructions']],
#         bulletType='1',
#     ))

#     # Cooking Notes
#     if recipe_data.get('cooking_notes'):
#         elements.append(Paragraph("Cooking Notes", styles["heading"]))
#         elements.append(ListFlowable(
#             [ListItem(Paragraph(item, styles["body"]), bulletType='bullet', leftIndent=10) for item in recipe_data['cooking_notes']],
#             bulletType='bullet',
#         ))

#     # Diet Information
#     if 'diet' in recipe_data:
#         elements.append(PageBreak())
#         elements.append(Paragraph("Diet", styles["heading"]))
#         diet_data = [[Paragraph(key, styles["body"]), Paragraph(str(value), styles["body"])]
#                      for section in recipe_data['diet'].values() for key, value in section.items()]
#         elements.append(generate_table(
#             [['Category', 'Value']] + diet_data,
#             col_widths=[1.5 * inch, 3 * inch],
#             styles=TableStyle([
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#                 ('FONTNAME', (0, 0), (-1, -1), DEFAULT_FONT),
#             ])
#         ))

#     # Nutritional Information
#     elements.append(PageBreak())
#     elements.append(Paragraph("Nutritional Information (per serving)", styles["heading"]))
#     nutrients = [['Nutrient', 'Amount', 'Percent of Daily Needs']] + [
#         [n['name'], f"{n['amount']:.2f} {n['unit']}", f"{n['percentOfDailyNeeds']:.2f}%"] for n in recipe_data['nutrients']
#     ]
#     elements.append(generate_table(
#         nutrients,
#         col_widths=[2.5 * inch, 2 * inch, 2 * inch],
#         styles=TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#             ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
#             ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
#             ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
#         ])
#     ))

#     # Build PDF
#     doc.build(elements)
#     logging.info(f"PDF generated: {filename}")


from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Register a compact font (e.g., Arial Narrow)
try:
    pdfmetrics.registerFont(TTFont('ArialNarrow', 'arialn.ttf'))
    pdfmetrics.registerFont(TTFont('ArialNarrow-Bold', 'arialnb.ttf'))
    FONT_NORMAL = "ArialNarrow"
    FONT_BOLD = "ArialNarrow-Bold"
except:
    logger.warning("Arial Narrow font not found. Using default fonts.")
    FONT_NORMAL = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

# Style definitions
def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontSize=18,  # Reduced from 24
            textColor=colors.darkblue,
            spaceAfter=8,   # Reduced from 12
            fontName=FONT_BOLD,
        ),
        "heading": ParagraphStyle(
            "HeadingStyle",
            parent=styles["Heading2"],
            fontSize=12,  # Reduced from 14
            textColor=colors.black,
            spaceBefore=8,  # Reduced from 12
            spaceAfter=4,   # Reduced from 6
            fontName=FONT_BOLD,
        ),
        "subheading": ParagraphStyle(
            "SubheadingStyle",
            parent=styles["Heading3"],
            fontSize=11,  # Reduced from 12
            textColor=colors.black,
            spaceBefore=4,   # Reduced from 6
            spaceAfter=4,   # Reduced from 6
            fontName=FONT_BOLD,
        ),
        "body": ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=9,   # Reduced from 10
            textColor=colors.black,
            spaceAfter=4,   # Reduced from 6
            fontName=FONT_NORMAL,
        ),
    }

# Generate ingredient section
def generate_ingredient_section(ingredients: Dict[str, List[str]], styles: Dict[str, ParagraphStyle]) -> List[Any]:
    elements = [Paragraph("Ingredients", styles["heading"])]
    for category, items in ingredients.items():
        elements.append(Paragraph(category, styles["subheading"]))
        elements.append(ListFlowable(
            [ListItem(Paragraph(item, styles["body"]), bulletType='bullet', bulletDedent='follow', leftIndent=20, bulletFontName=FONT_NORMAL) for item in items],
            bulletType='bullet', leftIndent=20, bulletFontName=FONT_NORMAL, start='circle' # change bullet type to circle
        ))
        elements.append(Spacer(1, 2)) # Reduce space after each list
    return elements

# Generate table
def generate_table(data: List[List[Any]], col_widths: List[float], styles: TableStyle) -> Table:
    table = Table(data, colWidths=col_widths, repeatRows=1) # repeat header row
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
    logger.info(f"Generating PDF for recipe: {recipe_data['title']}")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = get_styles()
    elements = []

    # Title
    elements.append(Paragraph(recipe_data['title'], styles["title"]))
    elements.append(Spacer(1, 6)) # add space below the title

    # Ingredients
    elements.extend(generate_ingredient_section(recipe_data['ingredients'], styles))

    # Instructions
    elements.append(PageBreak())
    elements.append(Paragraph("Instructions", styles["heading"]))
    elements.append(ListFlowable(
        [ListItem(Paragraph(item, styles["body"]), bulletType='1', bulletDedent='follow', leftIndent=20, bulletFontName=FONT_NORMAL) for item in recipe_data['instructions']],
        bulletType='1', leftIndent=20, bulletFontName=FONT_NORMAL
    ))

    # Cooking Notes
    if recipe_data.get('cooking_notes'):
        elements.append(Paragraph("Cooking Notes", styles["heading"]))
        elements.append(ListFlowable(
            [ListItem(Paragraph(item, styles["body"]), bulletType='bullet', bulletDedent='follow', leftIndent=20, bulletFontName=FONT_NORMAL, start='circle') for item in recipe_data['cooking_notes']],
            bulletType='bullet', leftIndent=20, bulletFontName=FONT_NORMAL, start='circle'
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
                ('FONTNAME', (0, 0), (-1, -1), FONT_NORMAL),
                ('FONTSIZE', (0, 0), (-1, -1), 9), # set font size to 9
                ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Reduce left padding
                ('RIGHTPADDING', (0, 0), (-1, -1), 3), # Reduce right padding
                ('TOPPADDING', (0, 0), (-1, -1), 1),   # Reduce top padding
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),# Reduce bottom padding
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
        col_widths=[2 * inch, 1.5 * inch, 2 * inch], # reduced column width
        styles=TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 0), (-1, -1), 9), # set font size to 9
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), # thin grid lines
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Reduce left padding
            ('RIGHTPADDING', (0, 0), (-1, -1), 3), # Reduce right padding
            ('TOPPADDING', (0, 0), (-1, -1), 1),   # Reduce top padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),# Reduce bottom padding
        ])
    ))

    # Build PDF
    doc.build(elements)
    logger.info(f"PDF generated: {filename}")