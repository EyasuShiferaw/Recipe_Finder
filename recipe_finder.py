import os 
import logging
import requests
from dotenv import load_dotenv
from functools import lru_cache
from prompt import extract_user_prompt, extract_system_prompt
from utility import get_completion, xml_extract_ingredients

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 

RECIPE_API = os.environ.get("spoonacular_API") 

class RecipeFinder:
    def __init__(self,user_query: str):
       self.user_query = user_query
       self.ingredients = None
       self.recipe_id = None
      

    def __call__(self):
        self.extract_ingredients()
        self.recipe = self.extract_recipe()
        self.recipe_id = self.recipe[0]["id"]
        self.recipe_info = self.extract_recipe_info()
        self.instructions = self.extract_recipe_instructions() 

    def __str__(self):
        return f"AdGenerator(business_details={self.business_details}, keywords={self.keywords})"


    @lru_cache(maxsize=1000)
    def construct_messages(self, user_prompt: str, system_prompt: str) -> list[dict]:
        """
        Construct the system and user prompts for the OpenAI API.
        
        Args:
            business_details (str): The business details.
            keywords (str): The keywords.
        
        Returns:
            list: A list of dictionaries representing the system and user prompts.
        """
        logger.info(f"constructing messages")
        messages = [
            {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        logger.info(f"Finished constructing messages")
        return messages
    
    def extract_ingredients(self) -> str:
        """
        Extract the ingredients from the user query.
        Returns:
            str: The extracted ingredients.
        """ 
        logger.info(f"extracting ingredients")
        user_prompt = extract_user_prompt.format(user_query=self.user_query)
        messages = self.construct_messages(extract_system_prompt, user_prompt)
        if not isinstance(messages, list):
            logger.error("Can't construct messages")
            return None
        try:
            self.ingredients = get_completion(messages)
        except Exception as e:
            logger.error(f"Can't extract ingredients\nException: {e}")
            return None
        else:
            logger.info("successfully extracted ingredients")
        
    
    def extract_recipe(self) -> str:
        
        logger.info(f"extracting recipe")
        if self.ingredients is None:
            logger.error("can't extract ingredients from the user query")
            return None
        
        ingredients = xml_extract_ingredients(self.ingredients)

        url = "https://api.spoonacular.com/recipes/findByIngredients"

        params = {
        "apiKey": RECIPE_API,
        "ingredients": ingredients,  
        "number": 1,                          

     }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print(f"Failed to fetch analyzed instructions: {response.status_code}, {response.text}")
            return None
        
    def extract_recipe_info(self) -> str:
        logger. info(f"extracting recipe info")
        base_url = "https://api.spoonacular.com/recipes/{id}/information"
        if self.recipe_id is None:
            logger.error("can't extract recipe info")
            return None
        
        url = base_url.replace("{id}", str(self.recipe_id))

        params = {
        "apiKey": RECIPE_API,
        'includeNutrition': True

     }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print(f"Failed to fetch information: {response.status_code}, {response.text}")
            return None
    

    def extract_recipe_instructions(self) -> str:

        logger. info(f"extracting recipe instructions")
        base_url = "https://api.spoonacular.com/recipes/{id}/analyzedInstructions"
        if self.recipe_id is None:
            logger.error("can't extract recipe instructions")
            return None
        
        url = base_url.replace("{id}", str(self.recipe_id))

        params = {
        "apiKey": RECIPE_API
     }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print(f"Failed to fetch analyzed instructions: {response.status_code}, {response.text}")
            return None

    
    # def extract_instructions(self) -> str:
    #     pass
    
    # def extract_nutrition_info(self) -> str:
    #     pass
    
    # def generate_ad(self) -> str:
    #     """
    #     Generate a cover letter based on the provided job description and resume.
    #     Args:
    #         messages (list[dict]): The messages.
        
    #     Returns:
    #         str: The generated ad.
    #     """ 
    #     messages = self.construct_messages()
    #     if not isinstance(messages, list):
    #         logger.error("Can't construct messages")
    #         return None
     
    #     try:
    #         self.ad = get_completion(messages)
    #     except Exception as e:
    #         logger.error(f"Can't generate ad\nException: {e}")
    #         return None
    #     else:
    #         logger.info("successfully generated ad")
    #     return self.ad


test = " Items I have include chicken breast, tomatoes, spinach, garlic, pasta, and Parmesan cheese"
test_recipe = RecipeFinder(test)
test_recipe()
