import os
import pickle
import torch
from torchvision import transforms
from PIL import Image
from Foodimg2Ing.args import get_parser
from Foodimg2Ing.model import get_model
from Foodimg2Ing.utils.output_utils import prepare_output
from Foodimg2Ing import app
from Foodimg2Ing.utils.generate_recipe import generate_recipe


def output(uploadedfile, user_data=None):
    """
    Process an uploaded food image with optional user data for personalization:
    1. Extract ingredients using the pretrained vision model.
    2. Send ingredients + user data to Gemini for personalized recipe generation.
    """

    try:
        # Paths
        data_dir = os.path.join(app.root_path, 'data')
        model_path = os.path.join(data_dir, 'modelbest.ckpt')

        # Check if required files exist
        if not os.path.exists(model_path):
            return "Error: Model file not found", [], []

        # Load vocabs
        ingrs_vocab = pickle.load(open(os.path.join(data_dir, 'ingr_vocab.pkl'), 'rb'))
        vocab = pickle.load(open(os.path.join(data_dir, 'instr_vocab.pkl'), 'rb'))

        ingr_vocab_size = len(ingrs_vocab)
        instrs_vocab_size = len(vocab)

        # Device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Model
        args = get_parser()
        args.maxseqlen = 15
        args.ingrs_only = False
        model = get_model(args, ingr_vocab_size, instrs_vocab_size)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()

        # Transform image
        transf = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])
        img = Image.open(uploadedfile).convert("RGB")
        image_tensor = transf(img).unsqueeze(0).to(device)

        # Predict ingredients (ignore local recipe generation)
        with torch.no_grad():
            outputs = model.sample(image_tensor, greedy=True, temperature=1.0, beam=-1, true_ingrs=None)
        ingr_ids = outputs['ingr_ids'].cpu().numpy()
        outs, valid = prepare_output(outputs['recipe_ids'][0], ingr_ids[0], ingrs_vocab, vocab)

        # Ingredients list
        ingredients_list = outs['ingrs']

        if not ingredients_list or len(ingredients_list) == 0:
            return "Error: No ingredients detected", [], []

        # Build Gemini prompt with user data
        prompt = (
            f"Generate a healthy recipe using these ingredients: {', '.join(ingredients_list)}. "
        )
        
        # Add user context if available
        if user_data:
            prompt += (
                f"User preferences: {user_data.get('diet', '')} diet, "
                f"allergies: {user_data.get('allergies', 'None')}, "
                f"goal: {user_data.get('goal', '')}, "
                f"cooking skill level: {user_data.get('skill', '')}. "
                f"Please consider these dietary restrictions and preferences when creating the recipe. "
            )
        
        prompt += (
            "Format the output as:\n"
            "title: <recipe title>\n"
            "ingredients:\n- item with quantity\n- item with quantity\n"
            "directions:\n1. step\n2. step\n"
            "Make sure the recipe is appropriate for the user's skill level and dietary needs."
        )

        # Call Gemini WITH USER DATA
        recipe = generate_recipe(prompt, user_data)

        # Ensure we return proper values even if some are missing
        title = recipe.get("title", "Recipe Title Not Generated")
        ingredients = recipe.get("ingredients", [])
        directions = recipe.get("directions", [])

        return title, ingredients, directions

    except Exception as e:
        print(f"Error in output function: {str(e)}")
        return f"Error: {str(e)}", [], []