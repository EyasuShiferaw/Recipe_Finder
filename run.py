import os
import logging
from pathlib import Path
from para2pdf import generate_pdf_report
from ad_generator import AdGenerator



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 


def main():

    business_details = os.environ.get('business_details', 'default_value')
    keywords = os.environ.get('keywords', 'default_value')


    if business_details == 'default_value' or business_details == '':
        logger.error(f"Can't generate ad, please provide business_details")
        return f"Can't generate ad, please provide business_details"
    if keywords == 'default_value' or keywords == '':
        logger.error(f"Can't generate ad, please provide keywords")
        return f"Can't generate ad, please provide keywords"
    

    ad_generator = AdGenerator(business_details, keywords)
    ad = ad_generator()
    
    if ad is None:
        logger.error(f"Can't generate ad")
        ad = f"Can't generate ad"
    
   # Get the directory of the current script (run.py)
    script_dir = Path(__file__).parent

    # Define the path for the 'output' folder inside the script's directory
    output_dir = script_dir / 'output'
    output_dir.mkdir(exist_ok=True)  # Create 'output' directory if it doesn't exist

    # Define the file path within the 'output' directory
    output_file = output_dir / 'result.pdf'

    generate_pdf_report(ad, output_file)
    

if __name__ == "__main__":
    main()    

