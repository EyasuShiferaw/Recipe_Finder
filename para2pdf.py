import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    ListFlowable, ListItem, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, Any, List, Optional
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors

import logging
import matplotlib.pyplot as plt
import io
import requests
import numpy as np

# Logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



def get_advanced_styles():
    """Create advanced paragraph styles."""
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "AdvancedTitleStyle",
            parent=styles["Title"],
            fontSize=22,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=12,
            fontName='Times-Bold',
            alignment=0,  # Left alignment
            leftIndent=0,  # Remove left indentation
            rightIndent=0  # Remove right indentation
        ),
        "subtitle": ParagraphStyle(
            "SubtitleStyle",
            parent=styles["Normal"],
            fontSize=14,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=6,
            fontName='Times-Roman',
            alignment=0,  # Left alignment
            leftIndent=0,
            rightIndent=0
        ),
        "heading": ParagraphStyle(
            "AdvancedHeadingStyle",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor('#2980B9'),
            spaceBefore=12,
            spaceAfter=6,
            fontName='Times-Bold',
            alignment=0,  # Left alignment
            leftIndent=0,
            rightIndent=0
        ),
        "body": ParagraphStyle(
            "AdvancedBodyStyle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Times-Roman',
            leading=14,
            alignment=0,  # Left alignment
            leftIndent=0,
            rightIndent=0
        )
    }


def create_nutritional_pie_chart(nutrients: List[Dict[Any, Any]]) -> Optional[str]:
    """
    Create a pie chart for nutritional information with unique colors.
    
    Args:
        nutrients (List[Dict]): List of nutrient dictionaries
    
    Returns:
        Optional[str]: Path to pie chart image
    """
    try:
        # Filter top nutrient contributors
        top_nutrients = [n for n in nutrients if n['percentOfDailyNeeds'] > 10]
        
        # Extract names and percentages
        labels = [n['name'] for n in top_nutrients]
        sizes = [n['percentOfDailyNeeds'] for n in top_nutrients]

        # Comprehensive color palette with distinct colors
        nutrient_colors = {
            'Protein': '#FF6B6B',      # Vibrant Red
            'Calcium': '#4ECDC4',       # Teal
            'Iron': '#45B7D1',          # Sky Blue
            'Vitamin A': '#FDCB6E',     # Golden Yellow
            'Vitamin C': '#6C5CE7',     # Purple
            'Vitamin D': '#FFA726',     # Orange
            'Vitamin B6': '#2ECC71',    # Bright Green
            'Magnesium': '#9C27B0',     # Deep Purple
            'Zinc': '#FF5722',          # Deep Orange
            'Potassium': '#795548'      # Brown
        }

        # Map colors to nutrients, use a default color if not in dictionary
        default_colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6']
        colors = [nutrient_colors.get(label, default_colors[i % len(default_colors)]) 
                  for i, label in enumerate(labels)]

        plt.figure(figsize=(10, 6))
        
        # Pie chart on the left side
        plt.subplot(121)
        plt.pie(sizes, colors=colors, startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
        plt.title('Nutritional Breakdown', fontsize=12)
        plt.axis('equal')

        # Legend on the right side
        plt.subplot(122)
        plt.axis('off')
        legend_labels = [f'{label}: {size:.1f}%' for label, size in zip(labels, sizes)]
        legend_colors = [plt.Rectangle((0,0),1,1, color=color) for color in colors]
        plt.legend(legend_colors, legend_labels, loc='center left', bbox_to_anchor=(0, 0.5))

        # Adjust layout and save
        plt.tight_layout()
        chart_filename = 'nutritional_chart.png'
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_filename
    except Exception as e:
        logger.error(f"Pie chart creation failed: {e}")
        return None


def create_ingredients_table(ingredients: Dict[str, List[str]], styles: Dict) -> List:
    """
    Create a visually appealing ingredients table using exact input data.
    
    Args:
        ingredients (Dict): Dictionary of ingredient categories and lists
        styles (Dict): Dictionary of paragraph styles
    
    Returns:
        List of table elements for PDF
    """
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib import colors

    # Prepare table data
    table_data = [['Ingredient', 'Details']]

    # Process each ingredient category
    for category, items in ingredients.items():
        # Add category header
        table_data.append([
            category.upper(), 
            ''
        ])
        
        for item in items:
            # Split ingredient into main part and details
            parts = item.split(',')
            ingredient = parts[0].strip()
            details = parts[1].strip() if len(parts) > 1 else ''
            
            table_data.append([
                ingredient,
                details
            ])

    # Create the table
    table = Table(table_data, colWidths=[250, 300])
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        
        # Category rows
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0,1), (-1,1), colors.whitesmoke),
        ('FONTNAME', (0,1), (-1,1), 'Times-Bold'),
        
        # Data rows
        ('BACKGROUND', (0,2), (-1,-1), colors.HexColor('#ECF0F1')),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,2), (-1,-1), 10),
    ]))

    return [
        Paragraph("Ingredients", styles["heading"]),
        table
    ]
      

def create_recipe_pdf(recipe_data: Dict[str, Any], output_filename: str ):
    """
    Generate a comprehensive PDF for the Bruschetta Pork Pasta recipe.
    
    Args:
        recipe_data (Dict): Complete recipe information
        output_filename (str): Filename for the PDF
    """
    # Register fonts
    # register_fonts()
    
    # Prepare styles
    styles = get_advanced_styles()
    
    # PDF Document Setup
    doc = SimpleDocTemplate(
        output_filename, 
        pagesize=letter, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=72, 
        bottomMargin=18
    )
    
    elements = []
    
    
    # Title and Summary
    elements.append(Paragraph(recipe_data['title'], styles["title"]))
    elements.append(Paragraph(recipe_data.get('summary', ''), styles["subtitle"]))
    elements.append(Spacer(1, 12))
    
    # Ingredients Section
    elements.append(Paragraph("Ingredients", styles["heading"]))
    for category, items in recipe_data['ingredients'].items():
        elements.append(Paragraph(category, styles["subtitle"]))
        elements.append(ListFlowable(
            [ListItem(Paragraph(item, styles["body"]), bulletType='bullet') for item in items],
            bulletType='bullet'
        ))



    # Instructions Section
    elements.append(Paragraph("Cooking Instructions", styles["heading"]))
    elements.append(ListFlowable(
        [ListItem(Paragraph(instruction, styles["body"]), bulletType='bullet') 
        for instruction in recipe_data.get('instructions', [])],
        bulletType='bullet'
    ))    
    
    # Cooking Notes
    if recipe_data.get('cooking_notes'):
        elements.append(Paragraph("Cooking Tips", styles["heading"]))
        elements.append(ListFlowable(
            [ListItem(Paragraph(note, styles["body"]), bulletType='bullet') for note in recipe_data['cooking_notes']],
            bulletType='bullet'
        ))
    
    # Nutritional Pie Chart
    elements.append(PageBreak())
    elements.append(Paragraph("Nutritional Insights", styles["heading"]))
    
    # Create and add nutritional pie chart
    chart_path = create_nutritional_pie_chart(recipe_data['nutrients'])
    if chart_path:
        chart_image = Image(chart_path, width=6*inch, height=4.5*inch)
        chart_image.hAlign = 'CENTER'
        elements.append(chart_image)
    
    # Dietary Information
    if recipe_data.get('diet'):
        elements.append(Paragraph("Dietary Information", styles["heading"]))
        diet_info = recipe_data['diet']
        
        # Create diet table
        diet_data = []
        for section_name, section_data in diet_info.items():
            diet_data.append([section_name, ''])
            for key, value in section_data.items():
                diet_data.append([key, str(value)])
        
        diet_table = Table(diet_data, colWidths=[2*inch, 4*inch])
        diet_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (0, -1), colors.beige),
        ]))
        elements.append(diet_table)
    
    # Build PDF
    doc.build(elements)
    logger.info(f"PDF generated successfully: {output_filename}")
