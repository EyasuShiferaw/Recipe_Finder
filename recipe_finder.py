import os 
import logging
import requests
from dotenv import load_dotenv
from functools import lru_cache
from prompt import extract_user_prompt, extract_system_prompt, recipe_user_prompt, recipe_system_prompt
from utility import get_completion, xml_extract_ingredients, parse_recipe

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 

RECIPE_API = os.environ.get("spoonacular_API") 

class RecipeFinder:
    def __init__(self,user_query: str):
       self.user_query = user_query
       self.diet = None
       self.title = None
       self.image = None
       self.recipe_data = None
       self.ingredients = None
       self.recipe_id = None
       self.nutrients = None

       
      
    @lru_cache(maxsize=1000)
    def __call__(self):
        self.extract_ingredients()
        self.recipe = self.extract_recipe()
        self.recipe_id = self.recipe[0]["id"]
        self.title = self.recipe[0]["title"]
        self.image = self.recipe[0]["image"]
        self.recipe_info = self.extract_recipe_info()
        self.summary = self.recipe_info["summary"]
        self.instructions = self.recipe_info["instructions"]
        self.ingredient_info = self.ingredients_info(self.recipe)
        self.nutrients = self.extract_recipe_nutrients(self.recipe_info) 
        self.diet= self.diet_info(self.recipe_info)
        self.temp = self.full_instruction( self.summary, self.ingredient_info, self.instructions)
        self.recipe_data = parse_recipe(self.temp)

        self.enrich_recipe()
        return self.recipe_data      
       

        print(self.recipe_data, self.temp)


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
        """Extract the recipe f.
        Returns:
            str: The extracted recipe."""
        
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
            return response.json()
        else:
            print(f"Failed to fetch analyzed instructions: {response.status_code}, {response.text}")
            return None
      
    def extract_recipe_info(self) -> list[dict]:
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
            return response.json()
        else:
            print(f"Failed to fetch information: {response.status_code}, {response.text}")
            return None
    

    def extract_recipe_nutrients(self, info:dict) -> list[dict]:

        logger. info(f"extracting recipe instructions")

        try:
            return  info["nutrition"]["nutrients"]
        except:
            return None

        
    def ingredients_info(self, recipe:str):

        usedIngredients = [i["original"] for i in recipe[0]["usedIngredients"]]
        missedIngredients = [i["original"] for i in recipe[0]["missedIngredients"]]
        unusedIngredients = [i["name"] for i in recipe[0]["unusedIngredients"]]
        
        return {"unusedIngredients": unusedIngredients,"usedIngredients": usedIngredients,"missedIngredients": missedIngredients} 

    def diet_info(self, recipe_data: dict):
                # Organize Diet Info
        diet_info = {
            "Dietary Suitability": {
                "Vegetarian": "Yes" if recipe_data['vegetarian'] else "No",
                "Vegan": "Yes" if recipe_data['vegan'] else "No",
                "Gluten-Free": "Yes" if recipe_data['glutenFree'] else "No",
                "Dairy-Free": "Yes" if recipe_data['dairyFree'] else "No",
                "Low FODMAP": "Yes" if recipe_data['lowFodmap'] else "No",
                "GAPS Diet": "Yes" if recipe_data['gaps'].lower() == 'yes' else "No"
            },
            "Health Metrics": {
                "Weight Watcher Smart Points": recipe_data['weightWatcherSmartPoints'],
                "Health Score": recipe_data['healthScore']
            },
            "Additional Notes": {
                "Very Healthy": "Yes" if recipe_data['veryHealthy'] else "No",
                "Sustainable": "Yes" if recipe_data['sustainable'] else "No"
            }
        }
        return diet_info

    def full_instruction(self, summary, ingredient, instruction):
        
        logger.info(f"generating full instruction")
        user_prompt = recipe_user_prompt.format(INSERT_SUMMARY=summary, INSERT_INGREDIENTS=ingredient["usedIngredients"], INSERT_ORIGINAL_INSTRUCTIONS=instruction)
        messages = self.construct_messages(recipe_system_prompt, user_prompt)
       
        
        try:
            response = get_completion(messages)
        except:
            logger.error("Can't generate full instruction")
            return None
        else:
            logger.info("successfully generated full instruction")
            print(response)
            return response
        
    def enrich_recipe(self) -> dict:
        """Enrich the parsed recipe data with additional details.
    
        
        Returns:
            dict: The enriched recipe dictionary.
        """
        try:
           
            self.recipe_data.update({
                "title": self.title,
                "image": self.image,
                "diet": self.diet,
                "nutrients": self.nutrients,
            })
            logger.info("Recipe successfully enriched with additional details.")
        except Exception as e:
            logger.error(f"Error enriching recipe data.\nException: {e}")
            raise
    


test = " Items I have include chicken breast, tomatoes, spinach, garlic, pasta, and Parmesan cheese"
test_recipe = RecipeFinder(test)

print(test_recipe(), test_recipe.recipe_data, (test_recipe.recipe_data).keys())

