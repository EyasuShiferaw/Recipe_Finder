from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, ListFlowable, ListItem, PageBreak, Frame,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus.paraparser import ParaParser
import requests
from io import BytesIO

# Improved font handling with fallback
DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_BOLD = "Helvetica-Bold"

if DEFAULT_FONT not in pdfmetrics.getRegisteredFontNames():
    DEFAULT_FONT = "Times-Roman"  # Common fallback
if DEFAULT_FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
    DEFAULT_FONT_BOLD = "Times-Bold" if "Times-Bold" in pdfmetrics.getRegisteredFontNames() else DEFAULT_FONT

class Utf8ParaParser(ParaParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoding = 'utf8' #explicitly setting the encoding.



def create_recipe_pdf(recipe_data, filename="recipe.pdf"):

        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Style definitions (with font fallbacks)
        title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=24, textColor=colors.darkblue, spaceAfter=12, fontName=DEFAULT_FONT_BOLD)
        heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=14, textColor=colors.black, spaceBefore=12, spaceAfter=6, fontName=DEFAULT_FONT_BOLD)
        subheading_style = ParagraphStyle("SubheadingStyle", parent=styles["Heading3"], fontSize=12, textColor=colors.black, spaceBefore=6, spaceAfter=6, fontName=DEFAULT_FONT_BOLD)
        body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=10, textColor=colors.black, spaceAfter=6, fontName=DEFAULT_FONT)

        # Title
        elements.append(Paragraph(recipe_data['title'], title_style))

        # Image (with placeholder and improved error handling)
        try:
            response = requests.get(recipe_data.get('image', ""), stream=True) # Placeholder image
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image(img_data, width=4*inch, height=3*inch, hAlign='CENTER')
            elements.append(img)
            elements.append(Spacer(1, 12))
        except requests.exceptions.RequestException as e:
            print(f"Image Error: {e}")
            # Placeholder if image retrieval fails
            elements.append(Paragraph("Image Not Available", body_style))
            elements.append(Spacer(1,12))
        except Exception as e:
            print(f"Image Processing Error: {e}")  # Handles other errors
            elements.append(Paragraph("Image Not Available", body_style))
            elements.append(Spacer(1, 12))

# Ingredients
        elements.append(Paragraph("Ingredients", heading_style))
        for category, items in recipe_data['ingredients'].items():
            elements.append(Paragraph(category, subheading_style))
            ingredient_list = ListFlowable(
                [ListItem(Paragraph(item, body_style), bulletType='bullet', leftIndent=10) for item in items],
                bulletType='bullet'
            )
            elements.append(ingredient_list)
            elements.append(Spacer(1, 6))  # Add some space after each ingredient category

        elements.append(PageBreak())  # Page break before instructions

        # Instructions
        elements.append(Paragraph("Instructions", heading_style))
        instruction_list = ListFlowable(
            [ListItem(Paragraph(item, body_style), bulletType='1', leftIndent=10) for item in recipe_data['instructions']],
            bulletType='1'
        )
        elements.append(instruction_list)
        elements.append(Spacer(1, 12))

        # Cooking Notes
        if recipe_data['cooking_notes']:
            elements.append(Paragraph("Cooking Notes", heading_style))
            notes_list = ListFlowable(
                [ListItem(Paragraph(item, body_style), bulletType='bullet', leftIndent=10) for item in recipe_data['cooking_notes']],
                bulletType='bullet'
            )
            elements.append(notes_list)
            elements.append(Spacer(1, 12))
        elements.append(PageBreak())  # Page break before 

        # Diet Section (improved with dynamic handling)
        if 'diet' in recipe_data:  # Check if diet information is present
            elements.append(Paragraph("Diet", heading_style))

            diet_data = []
            for section, items in recipe_data['diet'].items(): # Iterate through diet sections
                for key, value in items.items():
                    diet_data.append([Paragraph(key + ":", body_style), Paragraph(str(value), body_style)])

            diet_table = Table(diet_data, colWidths=[1.5 * inch, 3 * inch])
            diet_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(diet_table)
            elements.append(Spacer(1, 12))


        elements.append(PageBreak())  # Page break before 
        # Nutrients
        elements.append(Paragraph("Nutritional Information (per serving)", heading_style))
        nutrient_data = [
            [
                Paragraph(str(n['name']), body_style),
                Paragraph(f"{n['amount']:.2f} {n['unit']}", body_style),
                Paragraph(f"{n['percentOfDailyNeeds']:.2f}%", body_style),
            ] for n in recipe_data['nutrients']
        ]
        nutrient_table = Table([['Nutrient', 'Amount', 'Percent of Daily Needs']] + nutrient_data)
        nutrient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        elements.append(nutrient_table)

        doc.build(elements)