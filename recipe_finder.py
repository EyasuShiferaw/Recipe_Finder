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
        print(recipe)
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
        """
        Construct the system and user prompts for the OpenAI API.
        
        Args:
            company_name (str): The name of the company.
            job_description (str): The job description.
            resume (str): The resume.
        
        Returns:
            list: A list of dictionaries representing the system and user prompts.

        """
        logger.info("Constructing messages for the API.")
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def extract_ingredients(self) -> None:
        """
        Extract ingredients from the user query.

        """
        logger.info("Extracting ingredients from the user query.")
        user_prompt = extract_user_prompt.format(user_query=self.user_query)
        messages = self.construct_messages(extract_system_prompt, user_prompt)
        try:
            self.ingredients = get_completion(messages)
            logger.info("Successfully extracted ingredients.")
        except Exception as e:
            logger.error(f"Error extracting ingredients: {e}")


    def extract_recipe(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch recipe based on extracted ingredients.

        Returns:
            list: A list of dictionaries representing the recipe.
        """
        logger.info("Fetching recipe based on extracted ingredients.")
        if not self.ingredients:
            logger.error("Ingredients are missing.")
            return None

        ingredients = xml_extract_ingredients(self.ingredients)
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {"apiKey": RECIPE_API,"ingredients": ingredients, "ranking": 1, "number": 1}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch recipe: {e}")
            return None

    def extract_recipe_info(self) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed recipe information.

        Returns:
            dict: A dictionary representing the detailed recipe information.
        """
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
        """
        Extract nutritional information from the recipe.

        Returns:
            list: A list of dictionaries representing the nutritional information.
        """

        logger.info("Extracting nutritional information.")
        return info.get("nutrition", {}).get("nutrients")

    def get_ingredients_info(self, recipe: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Organize ingredients information.

        Args:
            recipe (list): A list of dictionaries representing the recipe.

        Returns:
            dict: A dictionary representing the ingredients information.
        """

        logger.info("Organizing ingredients information.")
        used = [i["original"] for i in recipe[0].get("usedIngredients", [])]
        missed = [i["original"] for i in recipe[0].get("missedIngredients", [])]
        unused = [i["name"] for i in recipe[0].get("unusedIngredients", [])]
        return {"usedIngredients": used, "missedIngredients": missed, "unusedIngredients": unused}

    def get_diet_info(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract dietary suitability information.

        Args:
            recipe_data (dict): A dictionary representing the recipe data.

        Returns:
            dict: A dictionary representing the dietary suitability information.
        """

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
        """
        Generate complete recipe instructions.

        Args:
            summary (str): a summary of the instructions
            ingredients (dict): ingredients
            instructions (str): instructions

        Returns:
            str: A string representing the complete recipe instructions.

        """

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
        """
        Enrich the recipe data with additional information.

        """
        logger.info("Enriching the recipe data.")
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
