import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

def generate_recipe(prompt, user_data=None):
    """
    Generate recipe using Gemini API with optional user personalization
    """
    try:
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {
                "title": "API Key Missing",
                "ingredients": ["Please set GEMINI_API_KEY in your environment variables"],
                "directions": ["Contact administrator"]
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Enhanced prompt with strict formatting requirements
        formatted_prompt = f"""
        {prompt}
        
        CRITICAL: You MUST format your response EXACTLY as follows:
        
        Day X — Recipe Title
        Ingredients
        ['ingredient 1 with quantity', 'ingredient 2 with quantity', 'ingredient 3 with quantity']
        Directions
        ['Step 1 instruction', 'Step 2 instruction', 'Step 3 instruction']
        
        Do NOT add any extra text, explanations, or formatting beyond this structure.
        """
        
        # Generate response
        response = model.generate_content(formatted_prompt)
        
        if not response.text:
            return {
                "title": "No response from AI",
                "ingredients": [],
                "directions": []
            }
        
        # Parse the response
        return parse_recipe_response(response.text)
        
    except Exception as e:
        print(f"Error in generate_recipe: {str(e)}")
        return {
            "title": f"Error: {str(e)}",
            "ingredients": [],
            "directions": []
        }

def parse_recipe_response(response_text):
    """
    Parse the Gemini response into structured recipe data
    Handles the format: "Day X — Title", Ingredients list, Directions list
    Converts arrays to HTML-friendly format with <li> tags
    """
    recipe = {
        "title": "",
        "ingredients": [],
        "directions": []
    }
    
    try:
        lines = [line.strip() for line in response_text.strip().split('\n') if line.strip()]
        
        # Extract title (first line) - remove duplicate "Day X —" if present
        if lines:
            title = lines[0]
            # Remove duplicate "Day X —" patterns
            title = re.sub(r'(Day \d+ — )+', 'Day \\1 — ', title)
            recipe["title"] = title
        
        # Find ingredients section
        ingredients_start = None
        directions_start = None
        
        for i, line in enumerate(lines):
            if line.lower().startswith('ingredients'):
                ingredients_start = i
            elif line.lower().startswith('directions'):
                directions_start = i
                break
        
        # Parse ingredients (array format)
        if ingredients_start is not None and directions_start is not None:
            # Extract ingredients array
            ingredients_text = ' '.join(lines[ingredients_start+1:directions_start])
            # Parse Python list format
            ingredients_match = re.search(r'\[(.*?)\]', ingredients_text, re.DOTALL)
            if ingredients_match:
                ingredients_str = ingredients_match.group(1)
                # Split by commas but handle quoted strings properly
                ingredients_list = [ing.strip().strip("'\"") for ing in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", ingredients_str) if ing.strip()]
                # Convert to HTML format with bullet points
                recipe["ingredients"] = format_as_html_list(ingredients_list)
        
        # Parse directions (array format)
        if directions_start is not None:
            # Extract directions array
            directions_text = ' '.join(lines[directions_start+1:])
            directions_match = re.search(r'\[(.*?)\]', directions_text, re.DOTALL)
            if directions_match:
                directions_str = directions_match.group(1)
                # Split by commas but handle quoted strings properly
                directions_list = [dir.strip().strip("'\"") for dir in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", directions_str) if dir.strip()]
                # Convert to HTML format with numbered steps
                recipe["directions"] = format_as_html_list(directions_list, numbered=True)
        
        # Fallback parsing if array format fails
        if not recipe["ingredients"]:
            ingredients_list = parse_ingredients_fallback(lines, ingredients_start, directions_start)
            recipe["ingredients"] = format_as_html_list(ingredients_list)
        
        if not recipe["directions"]:
            directions_list = parse_directions_fallback(lines, directions_start)
            recipe["directions"] = format_as_html_list(directions_list, numbered=True)
        
        return recipe
        
    except Exception as e:
        print(f"Error parsing recipe response: {str(e)}")
        print(f"Raw response: {response_text}")
        recipe["title"] = "Parsing Error"
        recipe["directions"] = ["Failed to parse recipe. Please try again."]
        return recipe

def format_as_html_list(items, numbered=False):
    """
    Convert a list of items to HTML format with <li> tags
    """
    if not items:
        return ""
    
    if numbered:
        # For directions: create numbered list
        html_list = ""
        for i, item in enumerate(items, 1):
            html_list += f"{i}. {item}<br>"
        return html_list
    else:
        # For ingredients: create bullet points
        html_list = ""
        for item in items:
            html_list += f"• {item}<br>"
        return html_list

def parse_ingredients_fallback(lines, ingredients_start, directions_start):
    """Fallback method to parse ingredients if array format fails"""
    ingredients = []
    if ingredients_start is not None and directions_start is not None:
        for i in range(ingredients_start + 1, directions_start):
            line = lines[i].strip()
            if line and not line.lower().startswith('directions'):
                # Remove bullet points, numbers, or dashes
                clean_line = re.sub(r'^[\-\*•\d\.\s]+', '', line)
                if clean_line:
                    ingredients.append(clean_line)
    return ingredients

def parse_directions_fallback(lines, directions_start):
    """Fallback method to parse directions if array format fails"""
    directions = []
    if directions_start is not None:
        for i in range(directions_start + 1, len(lines)):
            line = lines[i].strip()
            if line and not re.match(r'^\s*$', line):
                # Remove numbering if present
                clean_line = re.sub(r'^\d+\.\s*', '', line)
                if clean_line:
                    directions.append(clean_line)
    return directions