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



def parse_xml(xml_string: str) -> list[dict]:
    """ Parse the XML string into a list of dictionaries.
    
    Args:
        xml_string (str): The XML string to parse.
    
    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains the following keys:
            - StrategyName: The name of the strategy.
            - Headlines: A list of headlines.
            - Description: The description of the strategy.
            - Explanation: The explanation of the strategy. 
    """
   
    ad_concepts = []

    try:
        tree = ET.fromstring(xml_string)
    except Exception as e:
        logger.error(f"Error parsing XML string.\nException: {e}")
        raise
    else:  
        for concept_element in tree.findall('Concept'):
            concept_data = {}
            concept_data['StrategyName'] = concept_element.find('StrategyName').text
            concept_data['Headlines'] = [headline.text for headline in concept_element.find('Headlines').findall('Headline')]
            concept_data['Description'] = concept_element.find('Description').text
            concept_data['Explanation'] = concept_element.find('Explanation').text
            ad_concepts.append(concept_data)

    return ad_concepts

def pipeline_for_xml_parse(xml_data: str) -> list[dict]:
    """ A pipeline for parsing XML data.

    Args:
        xml_data (str): The XML data to parse.
    
    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains the following keys:
            - StrategyName: The name of the strategy.
            - Headlines: A list of headlines.
            - Description: The description of the strategy.
            - Explanation: The explanation of the strategy.
    """
    logger.info(f"Parsing XML string")  
    ad_concepts = []
    try:
        cleaned_xml_data = get_xml_data(xml_data)
        ad_concepts = parse_xml(cleaned_xml_data)
    except Exception as e:
        logger.error(f"Error in pipeline for XML parse.\nException: {e}")
        raise
    else:
        logger.info(f"Successfully parsed XML data")
        return ad_concepts


# test = """
# <?xml version="1.0" encoding="UTF-8"?>
# <ingredient_extraction>
#     <ingredients>
#         <ingredient>Chicken Breast</ingredient>
#         <ingredient>Tomatoes</ingredient>
#         <ingredient>Spinach</ingredient>
#         <ingredient>Garlic</ingredient>
#         <ingredient>Pasta</ingredient>
#         <ingredient>Parmesan Cheese</ingredient>
#     </ingredients>
# </ingredient_extraction>
# """
# print(xml_extract_ingredients(test))

    