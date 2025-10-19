import os
import json
import re
import numpy as np
import tensorflow as tf
from PIL import Image
from scipy.spatial.distance import cosine
import pickle

# Load DenseNet201 model once
model = tf.keras.applications.DenseNet201(
    include_top=False, weights='imagenet', input_shape=(256, 256, 3), pooling='avg'
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENCODINGS_PATH = os.path.join(BASE_DIR, 'encodings.txt')
ENC_NAMES_PATH = os.path.join(BASE_DIR, 'enc_names.txt')
RECIPES_JSON = os.path.join(BASE_DIR, '..', 'static', 'main', 'indian_recipes.json')

# Load precomputed embeddings and names
with open(ENCODINGS_PATH, 'rb') as fp:
    enc_list = np.array(pickle.load(fp))
with open(ENC_NAMES_PATH, 'rb') as fp:
    names_list = pickle.load(fp)

def get_encodings(img: Image.Image):
    """Extract DenseNet encoding from a PIL image."""
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.keras.preprocessing.image.smart_resize(img_array, size=(256, 256))
    img_array = np.expand_dims(img_array, axis=0)
    img_preprocessed = tf.keras.applications.densenet.preprocess_input(img_array)
    encoding = model.predict(img_preprocessed)
    return encoding.flatten()

def get_similar_recipes(img):
    """Find top similar recipes from the dataset."""
    enc = get_encodings(img)
    similarity_list = []

    for i in range(len(enc_list)):
        similarity = cosine(enc_list[i].flatten(), enc.flatten())
        similarity_list.append(1 - similarity)

    sorted_list = sorted(zip(similarity_list, names_list), reverse=True)
    recipe_names = []
    for _, name in sorted_list:
        clean_name = re.sub(r'[0-9]+.jpg', "", name)
        if clean_name not in recipe_names:
            recipe_names.append(clean_name)
        if len(recipe_names) >= 10:
            break
    return recipe_names

def generate_recipe_from_image(image_path):
    """Full pipeline: image → structured recipe list for template."""
    try:
        img = Image.open(image_path)
        top_recipes = get_similar_recipes(img)

        with open(RECIPES_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)

        results = []
        for name in top_recipes[:10]:  # top 10 suggestions
            matches = [r for r in data if r["name"] == name]
            if matches:
                r = matches[0]
                # Make sure you pass the details in the order your template expects
                results.append([
                    r['name'].title(),      # Recipe Name
                    r['calories'],          # Calories
                    r['ingredients'],       # Ingredients
                    r['cooking_time'],      # Cooking Time
                    r['directions'],        # Directions
                    ""                      # Optional extra field if template expects it
                ])
        return results

    except Exception as e:
        return [["Error", "", "", "", str(e), ""]]
