import os
import logging
import aisuite as ai
from dotenv import load_dotenv


from bs4 import BeautifulSoup
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



def parse_recipe(xml_content: str) -> dict:
    """ Parse the recipe from the given XML content using BeautifulSoup.
    
    Args:
        xml_content(str): content in the xml format
    
    Returns:
        dict: The extracted recipe data.
    """
    logging.info(f"Parsing recipe from XML")
  
    try: 
        # Parse the XML content with BeautifulSoup
        soup = BeautifulSoup(xml_content, 'xml')
    except Exception as e:
        logger.error(f"Error parsing XML content with BeautifulSoup.\nException: {e}")
        return {}

    # Extract summary
    summary = soup.find('summary').text.strip() if soup.find('summary') else 'No summary provided'

    # Extract ingredients
    ingredients = {}
    
    for section in soup.find_all('section'):
        section_name = section.get('name', 'Unnamed Section')
        ingredients[section_name] = []
        
        for ingredient in section.find_all('ingredient'):
            name = ingredient.find('name').text.strip() if ingredient.find('name') else "Unknown"
            quantity = ingredient.find('quantity').text.strip() if ingredient.find('quantity') else "Unknown"
            notes = ingredient.find('notes').text.strip() if ingredient.find('notes') else ""
            
            ingredients[section_name].append(f"{quantity} {name}, {notes}")

    # Extract instructions
    instructions = []
    for step in soup.find_all('step'):
        instruction_text = step.find('instruction').text.strip() if step.find('instruction') else ''
        if instruction_text:
            instructions.append(instruction_text)

    # Extract cooking notes
    cooking_notes = []
    for note in soup.find_all('note'):
        note_text = note.text.strip() if note.text else ''
        if note_text:
            cooking_notes.append(note_text)

    # Construct result
    recipe_data = {
        'summary': summary,
        'ingredients': ingredients,
        'instructions': instructions,
        'cooking_notes': cooking_notes
    }

    logging.info(f"Successfully parsed recipe from XML")
    return recipe_data
