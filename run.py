import os
import logging
from pathlib import Path
from para2pdf import create_recipe_pdf
from Recipe_Finder.recipe_finder import RecipeFinder



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 


def main():

    ingredients = os.environ.get('ingredients', 'default_value')
   


    if ingredients == 'default_value' or ingredients == '':
        logger.error(f"Can't generate ad, please provide business_details")
        return f"Can't generate ad, please provide business_details"
    
    
    recipe = RecipeFinder(ingredients)
    recipe_data = recipe()
    
    
    if recipe_data is None:
        logger.error(f"Can't generate ad")
        ad = f"Can't generate ad"
    
   # Get the directory of the current script (run.py)
    script_dir = Path(__file__).parent

    # Define the path for the 'output' folder inside the script's directory
    output_dir = script_dir / 'output'
    output_dir.mkdir(exist_ok=True)  # Create 'output' directory if it doesn't exist

    # Define the file path within the 'output' directory
    output_file = str(output_dir / 'result.pdf')

    create_recipe_pdf(recipe_data, output_file)
    

if __name__ == "__main__":
    main()    

