import os
import pickle
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

def prepare_output(recipe_ids, ingr_ids, ingrs_vocab, vocab):
    """
    Prepare model output for display by converting IDs to text
    """
    try:
        # Filter out padding tokens and convert to text
        recipe_tokens = []
        for idx in recipe_ids:
            if idx == vocab.get('<end>', -1):
                break
            if idx != vocab.get('<start>', -1) and idx != vocab.get('<pad>', -1):
                recipe_tokens.append(vocab.get('idx2word', {}).get(idx, '<unk>'))
        
        # Convert ingredient IDs to text
        ingr_tokens = []
        for idx in ingr_ids:
            if idx == ingrs_vocab.get('</i>', -1):
                break
            if idx != ingrs_vocab.get('<start>', -1) and idx != ingrs_vocab.get('<pad>', -1):
                ingr_name = ingrs_vocab.get('idx2word', {}).get(idx, '<unk>')
                if ingr_name not in ['<start>', '</i>']:
                    ingr_tokens.append(ingr_name)
        
        # Remove duplicates from ingredients while preserving order
        seen = set()
        unique_ingrs = []
        for ingr in ingr_tokens:
            if ingr not in seen and ingr != '<unk>':
                seen.add(ingr)
                unique_ingrs.append(ingr)
        
        # Prepare output dictionary
        output = {
            'title': ' '.join(recipe_tokens[:10]) if recipe_tokens else 'Unknown Recipe',
            'ingrs': unique_ingrs,
            'instructions': ' '.join(recipe_tokens) if recipe_tokens else '',
            'recipe_tokens': recipe_tokens,
            'ingr_tokens': ingr_tokens
        }
        
        # Check if output is valid (has at least some ingredients)
        valid = len(unique_ingrs) > 0
        
        return output, valid
        
    except Exception as e:
        print(f"Error in prepare_output: {str(e)}")
        # Return empty but valid structure
        return {
            'title': 'Error',
            'ingrs': [],
            'instructions': '',
            'recipe_tokens': [],
            'ingr_tokens': []
        }, False

def decode_recipe(recipe_ids, vocab):
    """Decode recipe instruction IDs to text"""
    try:
        tokens = []
        for idx in recipe_ids:
            if idx == vocab.get('<end>', -1):
                break
            if idx not in [vocab.get('<start>', -1), vocab.get('<pad>', -1)]:
                word = vocab.get('idx2word', {}).get(idx, '<unk>')
                tokens.append(word)
        return ' '.join(tokens)
    except:
        return ""

def decode_ingredients(ingr_ids, ingrs_vocab):
    """Decode ingredient IDs to text"""
    try:
        ingredients = []
        for idx in ingr_ids:
            if idx == ingrs_vocab.get('</i>', -1):
                break
            if idx not in [ingrs_vocab.get('<start>', -1), ingrs_vocab.get('<pad>', -1)]:
                ingr = ingrs_vocab.get('idx2word', {}).get(idx, '<unk>')
                if ingr not in ['<start>', '</i>']:
                    ingredients.append(ingr)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_ingrs = []
        for ingr in ingredients:
            if ingr not in seen and ingr != '<unk>':
                seen.add(ingr)
                unique_ingrs.append(ingr)
        
        return unique_ingrs
    except:
        return []

def format_ingredients_for_display(ingredients_list):
    """Format ingredients list for nice display"""
    formatted = []
    for i, ingr in enumerate(ingredients_list, 1):
        formatted.append(f"{i}. {ingr.capitalize()}")
    return formatted