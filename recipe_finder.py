# import os 
# import logging
# import requests
# from dotenv import load_dotenv
# from functools import lru_cache
# from prompt import extract_user_prompt, extract_system_prompt, recipe_user_prompt, recipe_system_prompt
# from utility import get_completion, xml_extract_ingredients, parse_recipe

# load_dotenv()

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__) 

# RECIPE_API = os.environ.get("spoonacular_API") 

# class RecipeFinder:
#     def __init__(self,user_query: str):
#        self.user_query = user_query
#        self.diet = None
#        self.title = None
#        self.image = None
#        self.recipe_data = None
#        self.ingredients = None
#        self.recipe_id = None
#        self.nutrients = None

       
      
#     @lru_cache(maxsize=1000)
#     def __call__(self):
#         self.extract_ingredients()
#         self.recipe = self.extract_recipe()
#         self.recipe_id = self.recipe[0]["id"]
#         self.title = self.recipe[0]["title"]
#         self.image = self.recipe[0]["image"]
#         self.recipe_info = self.extract_recipe_info()
#         self.summary = self.recipe_info["summary"]
#         self.instructions = self.recipe_info["instructions"]
#         self.ingredient_info = self.ingredients_info(self.recipe)
#         self.nutrients = self.extract_recipe_nutrients(self.recipe_info) 
#         self.diet= self.diet_info(self.recipe_info)
#         self.temp = self.full_instruction( self.summary, self.ingredient_info, self.instructions)
#         self.recipe_data = parse_recipe(self.temp)

#         self.enrich_recipe()
#         return self.recipe_data      
       


#     @lru_cache(maxsize=1000)
#     def construct_messages(self, user_prompt: str, system_prompt: str) -> list[dict]:
#         """
#         Construct the system and user prompts for the OpenAI API.
        
#         Args:
#             business_details (str): The business details.
#             keywords (str): The keywords.
        
#         Returns:
#             list: A list of dictionaries representing the system and user prompts.
#         """
#         logger.info(f"constructing messages")
#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#             ]
#         logger.info(f"Finished constructing messages")
#         return messages
    
   
#     def extract_ingredients(self) -> str:
#         """
#         Extract the ingredients from the user query.
#         Returns:
#             str: The extracted ingredients.
#         """ 
#         logger.info(f"extracting ingredients")
#         user_prompt = extract_user_prompt.format(user_query=self.user_query)
#         messages = self.construct_messages(extract_system_prompt, user_prompt)
#         if not isinstance(messages, list):
#             logger.error("Can't construct messages")
#             return None
#         try:
#             self.ingredients = get_completion(messages)
#         except Exception as e:
#             logger.error(f"Can't extract ingredients\nException: {e}")
#             return None
#         else:
#             logger.info("successfully extracted ingredients")

    
#     def extract_recipe(self) -> str:
#         """Extract the recipe f.
#         Returns:
#             str: The extracted recipe."""
        
#         logger.info(f"extracting recipe")
#         if self.ingredients is None:
#             logger.error("can't extract ingredients from the user query")
#             return None
        
#         ingredients = xml_extract_ingredients(self.ingredients)

#         url = "https://api.spoonacular.com/recipes/findByIngredients"

#         params = {
#         "apiKey": RECIPE_API,
#         "ingredients": ingredients,  
#         "number": 1,                          

#      }
#         response = requests.get(url, params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"Failed to fetch analyzed instructions: {response.status_code}, {response.text}")
#             return None
      
#     def extract_recipe_info(self) -> list[dict]:
#         logger. info(f"extracting recipe info")
#         base_url = "https://api.spoonacular.com/recipes/{id}/information"
#         if self.recipe_id is None:
#             logger.error("can't extract recipe info")
#             return None
        
#         url = base_url.replace("{id}", str(self.recipe_id))

#         params = {
#         "apiKey": RECIPE_API,
#         'includeNutrition': True

#      }
#         response = requests.get(url, params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"Failed to fetch information: {response.status_code}, {response.text}")
#             return None
    

#     def extract_recipe_nutrients(self, info:dict) -> list[dict]:

#         logger. info(f"extracting recipe instructions")

#         try:
#             return  info["nutrition"]["nutrients"]
#         except:
#             return None

        
#     def ingredients_info(self, recipe:str):

#         usedIngredients = [i["original"] for i in recipe[0]["usedIngredients"]]
#         missedIngredients = [i["original"] for i in recipe[0]["missedIngredients"]]
#         unusedIngredients = [i["name"] for i in recipe[0]["unusedIngredients"]]
        
#         return {"unusedIngredients": unusedIngredients,"usedIngredients": usedIngredients,"missedIngredients": missedIngredients} 

#     def diet_info(self, recipe_data: dict):
#                 # Organize Diet Info
#         diet_info = {
#             "Dietary Suitability": {
#                 "Vegetarian": "Yes" if recipe_data['vegetarian'] else "No",
#                 "Vegan": "Yes" if recipe_data['vegan'] else "No",
#                 "Gluten-Free": "Yes" if recipe_data['glutenFree'] else "No",
#                 "Dairy-Free": "Yes" if recipe_data['dairyFree'] else "No",
#                 "Low FODMAP": "Yes" if recipe_data['lowFodmap'] else "No",
#                 "GAPS Diet": "Yes" if recipe_data['gaps'].lower() == 'yes' else "No"
#             },
#             "Health Metrics": {
#                 "Weight Watcher Smart Points": recipe_data['weightWatcherSmartPoints'],
#                 "Health Score": recipe_data['healthScore']
#             },
#             "Additional Notes": {
#                 "Very Healthy": "Yes" if recipe_data['veryHealthy'] else "No",
#                 "Sustainable": "Yes" if recipe_data['sustainable'] else "No"
#             }
#         }
#         return diet_info

#     def full_instruction(self, summary, ingredient, instruction):
        
#         logger.info(f"generating full instruction")
#         user_prompt = recipe_user_prompt.format(INSERT_SUMMARY=summary, INSERT_INGREDIENTS=ingredient["usedIngredients"], INSERT_ORIGINAL_INSTRUCTIONS=instruction)
#         messages = self.construct_messages(recipe_system_prompt, user_prompt)
       
        
#         try:
#             response = get_completion(messages)
#         except:
#             logger.error("Can't generate full instruction")
#             return None
#         else:
#             logger.info("successfully generated full instruction")
#             print(response)
#             return response
        
#     def enrich_recipe(self) -> dict:
#         """Enrich the parsed recipe data with additional details.
    
        
#         Returns:
#             dict: The enriched recipe dictionary.
#         """
#         try:
           
#             self.recipe_data.update({
#                 "title": self.title,
#                 "image": self.image,
#                 "diet": self.diet,
#                 "nutrients": self.nutrients,
#             })
#             logger.info("Recipe successfully enriched with additional details.")
#         except Exception as e:
#             logger.error(f"Error enriching recipe data.\nException: {e}")
#             raise
    


# # test = " Items I have include chicken breast, tomatoes, spinach, garlic, pasta, and Parmesan cheese"
# # test_recipe = RecipeFinder(test)

# # print(test_recipe(), test_recipe.recipe_data, (test_recipe.recipe_data).keys())



import os
import logging
import requests
from dotenv import load_dotenv
from functools import lru_cache
from typing import Optional, List, Dict, Any
from prompt import (
    extract_user_prompt,
    extract_system_prompt,
    recipe_user_prompt,
    recipe_system_prompt,
)
from utility import get_completion, xml_extract_ingredients, parse_recipe

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

RECIPE_API = os.getenv("spoonacular_API")

class RecipeFinder:
    def __init__(self, user_query: str):
        self.user_query = user_query
        self.diet: Optional[Dict[str, Any]] = None
        self.title: Optional[str] = None
        self.image: Optional[str] = None
        self.recipe_data: Optional[Dict[str, Any]] = None
        self.ingredients: Optional[str] = None
        self.recipe_id: Optional[int] = None
        self.nutrients: Optional[List[Dict[str, Any]]] = None

    @lru_cache(maxsize=1000)
    def __call__(self) -> Optional[Dict[str, Any]]:
        self.extract_ingredients()
        recipe = self.extract_recipe()
        if not recipe:
            logger.error("No recipe found.")
            return None

        self.recipe_id = recipe[0].get("id")
        self.title = recipe[0].get("title")
        self.image = recipe[0].get("image")

        recipe_info = self.extract_recipe_info()
        if not recipe_info:
            logger.error("Failed to fetch recipe info.")
            return None

        self.ingredients_info = self.get_ingredients_info(recipe)
        self.nutrients = self.extract_recipe_nutrients(recipe_info)
        self.diet = self.get_diet_info(recipe_info)
        
        summary = recipe_info.get("summary", "")
        instructions = recipe_info.get("instructions", "")
        self.recipe_data = parse_recipe(
            self.generate_full_instruction(summary, self.ingredients_info, instructions)
        )

        self.enrich_recipe()
        return self.recipe_data

    @lru_cache(maxsize=1000)
    def construct_messages(self, user_prompt: str, system_prompt: str) -> List[Dict[str, str]]:
        logger.info("Constructing messages for the API.")
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def extract_ingredients(self) -> None:
        logger.info("Extracting ingredients from the user query.")
        user_prompt = extract_user_prompt.format(user_query=self.user_query)
        messages = self.construct_messages(extract_system_prompt, user_prompt)
        try:
            self.ingredients = get_completion(messages)
            logger.info("Successfully extracted ingredients.")
        except Exception as e:
            logger.error(f"Error extracting ingredients: {e}")

    def extract_recipe(self) -> Optional[List[Dict[str, Any]]]:
        logger.info("Fetching recipe based on extracted ingredients.")
        if not self.ingredients:
            logger.error("Ingredients are missing.")
            return None

        ingredients = xml_extract_ingredients(self.ingredients)
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {"apiKey": RECIPE_API, "ingredients": ingredients, "number": 1}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch recipe: {e}")
            return None

    def extract_recipe_info(self) -> Optional[Dict[str, Any]]:
        logger.info("Fetching detailed recipe information.")
        if not self.recipe_id:
            logger.error("Recipe ID is missing.")
            return None

        url = f"https://api.spoonacular.com/recipes/{self.recipe_id}/information"
        params = {"apiKey": RECIPE_API, "includeNutrition": True}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch recipe info: {e}")
            return None

    def extract_recipe_nutrients(self, info: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        logger.info("Extracting nutritional information.")
        return info.get("nutrition", {}).get("nutrients")

    def get_ingredients_info(self, recipe: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        logger.info("Organizing ingredients information.")
        used = [i["original"] for i in recipe[0].get("usedIngredients", [])]
        missed = [i["original"] for i in recipe[0].get("missedIngredients", [])]
        unused = [i["name"] for i in recipe[0].get("unusedIngredients", [])]
        return {"usedIngredients": used, "missedIngredients": missed, "unusedIngredients": unused}

    def get_diet_info(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Extracting dietary suitability information.")
        return {
            "Dietary Suitability": {
                "Vegetarian": "Yes" if recipe_data.get("vegetarian") else "No",
                "Vegan": "Yes" if recipe_data.get("vegan") else "No",
                "Gluten-Free": "Yes" if recipe_data.get("glutenFree") else "No",
                "Dairy-Free": "Yes" if recipe_data.get("dairyFree") else "No",
                "Low FODMAP": "Yes" if recipe_data.get("lowFodmap") else "No",
            },
            "Health Metrics": {
                "Weight Watcher Smart Points": recipe_data.get("weightWatcherSmartPoints"),
                "Health Score": recipe_data.get("healthScore"),
            },
            "Additional Notes": {
                "Very Healthy": "Yes" if recipe_data.get("veryHealthy") else "No",
                "Sustainable": "Yes" if recipe_data.get("sustainable") else "No",
            },
        }

    def generate_full_instruction(self, summary: str, ingredients: Dict[str, List[str]], instructions: str) -> str:
        logger.info("Generating complete recipe instructions.")
        user_prompt = recipe_user_prompt.format(
            INSERT_SUMMARY=summary,
            INSERT_INGREDIENTS=ingredients["usedIngredients"],
            INSERT_ORIGINAL_INSTRUCTIONS=instructions,
        )
        messages = self.construct_messages(recipe_system_prompt, user_prompt)
        try:
            return get_completion(messages)
        except Exception as e:
            logger.error(f"Error generating instructions: {e}")
            return ""

    def enrich_recipe(self) -> None:
        if not self.recipe_data:
            logger.error("Recipe data is missing; cannot enrich.")
            return
        self.recipe_data.update({
            "title": self.title,
            "image": self.image,
            "diet": self.diet,
            "nutrients": self.nutrients,
        })
        logger.info("Successfully enriched the recipe data.")

# Example usage (commented out for production):
# query = "Items I have include chicken breast, tomatoes, spinach, garlic, pasta, and Parmesan cheese"
# recipe_finder = RecipeFinder(query)
# result = recipe_finder()
# print(result)