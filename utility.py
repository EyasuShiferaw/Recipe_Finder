import os
import re
import logging
import aisuite as ai
from dotenv import load_dotenv
from functools import lru_cache
import xml.etree.ElementTree as ET
from tenacity import retry, stop_after_attempt, wait_exponential


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 

# Load environment variables from .env file
load_dotenv()



@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def get_completion(messages: list[dict]) -> str:
    """ Generate a completion for the given messages and model.
    
    Args:
        messages (list): A list of messages, where each message is a dictionary with the following keys:
            - role: The role of the sender of the message, e.g. "user" or "system".
            - content: The text of the message.
        model (str): The model to use to generate the completion.
    
    Returns:
        str: The generated completion.
    """
    logger.info(f"Getting completion for messages:")
    client = ai.Client()
    client.configure({"openai" : {
  "api_key": os.environ.get("API_KEY"),
}})
    response = None
    model = "openai:gpt-4o"
    try:
        logger.info("Trying to get completion for messages")
        response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.75
            )
    except Exception as e:
        logger.error(f"Error getting completion for messages.\nException: {e}")
        raise  # Allow @retry to handle the exception
    else:
        logger.info(f"successfully got completion for messages")
        return response.choices[0].message.content
    

def get_xml_data(xml_data: str, start_tag: str, end_tag: str) -> str:
    """ Remove any unnecessary data from the given XML data.
    
    Args:
        xml_data (str): The XML data to remove unnecessary data from.
    
    Returns:
        str: The cleaned XML data.
    """

    try:
        start_index = xml_data.index(start_tag)
        end_index = xml_data.index(end_tag) + len(end_tag)
        xml_string = xml_data[start_index:end_index]
    except Exception as e:
        logger.error(f"Error cleaning XML data.\nException: {e}")
        raise
    else:
        logger.info(f"Successfully cleaned XML data")
        return xml_string    
    
def xml_extract_ingredients(xml_data: str) -> str:
    """ Extract the ingredients from the user query.
    
    Args:
        user_query (str): The user query.
    
    Returns:
        str: The extracted ingredients.
    """
    logger.info(f"Extracting ingredients from XML")
    start_tag = "<ingredient_extraction>"
    end_tag = "</ingredient_extraction>"
    xml_string = get_xml_data(xml_data, start_tag, end_tag)
    root = ET.fromstring(xml_string)

    # Extract ingredients
    try:
        ingredients = [ingredient.text for ingredient in root.findall('./ingredients/ingredient')]
    except Exception as e:
        logger.error(f"Error extracting ingredients from XML.\nException: {e}")
        raise
    else:
        logger.info(f"Successfully extracted ingredients from XML")
        return ",".join(ingredients)



def parse_recipe(xml_content):

    try: 
        root = ET.fromstring(xml_content)
    except Exception as e:
        start_tag = "<recipe>"
        end_tag = "</recipe>"
        xml_string = get_xml_data(xml_content, start_tag, end_tag)
        # Parse the XML content
        root = ET.fromstring(xml_string)

    # Extract summary
    summary = root.find('summary').text.strip()

    # Extract ingredients
    ingredients = {
        'Original Ingredients': [],
        'Additional Required Ingredients': []
    }
    
    for section in root.find('ingredients'):
        section_name = section.attrib['name']
        items = section.text.strip().split('\n')
        ingredients[section_name] = [item.strip('- ').strip() for item in items if item.strip()]

    # Extract instructions
    instructions = []
    for step in root.find('instructions'):
        instructions.append(step.text.strip())

    # Extract cooking notes
    cooking_notes = root.find('cooking-notes').text.strip().split('\n')
    cooking_notes = [note.strip('- ').strip() for note in cooking_notes if note.strip()]

    # Construct result
    recipe_data = {
        'summary': summary,
        'ingredients': ingredients,
        'instructions': instructions,
        'cooking_notes': cooking_notes
    }
    return recipe_data



    