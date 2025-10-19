from Foodimg2Ing import app
from flask import render_template,flash, request, redirect, url_for, session
from Foodimg2Ing.db import get_db_connection
from flask import Flask, render_template, request, redirect, url_for
import os  # <-- ✅ Add this line
from PIL import Image
import base64
from Foodimg2Ing.utils.photo_recipe import generate_recipe_from_image


# ---------------------------
# 1️⃣ AUTHENTICATION ROUTES
# ---------------------------

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            flash("All fields are required")
            return redirect(url_for('signup'))

        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password))
        connection.commit()
        cursor.close()
        connection.close()

        # ✅ Save email in session for onboarding
        session['user_email'] = email

        return redirect(url_for('onboarding_gender'))  # Start onboarding
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            # ✅ Store user_email in session
            session['user_email'] = email
            return redirect(url_for('home'))  # Redirect to home page after successful login
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))

    return render_template('login.html')


# ---------------------------
# 2️⃣ ONBOARDING FLOW ROUTES
# ---------------------------

@app.route('/onboarding/gender', methods=['GET', 'POST'])
def onboarding_gender():
    if request.method == 'POST':
        session['gender'] = request.form['gender']
        return redirect(url_for('onboarding_age'))
    return render_template('onboarding/gender.html')

@app.route('/onboarding/age', methods=['GET', 'POST'])
def onboarding_age():
    if request.method == 'POST':
        session['age'] = request.form['age']
        return redirect(url_for('onboarding_weight'))
    return render_template('onboarding/age.html')

@app.route('/onboarding/weight', methods=['GET', 'POST'])
def onboarding_weight():
    if request.method == 'POST':
        session['weight'] = request.form['weight']
        return redirect(url_for('onboarding_height'))
    return render_template('onboarding/weight.html')

@app.route('/onboarding/height', methods=['GET', 'POST'])
def onboarding_height():
    if request.method == 'POST':
        session['height'] = request.form['height']
        return redirect(url_for('onboarding_skill'))
    return render_template('onboarding/height.html')

@app.route('/onboarding/skill', methods=['GET', 'POST'])
def onboarding_skill():
    if request.method == 'POST':
        session['skill'] = request.form['skill']
        return redirect(url_for('onboarding_allergies'))
    return render_template('onboarding/skill.html')

@app.route('/onboarding/allergies', methods=['GET', 'POST'])
def onboarding_allergies():
    if request.method == 'POST':
        session['allergies'] = request.form['allergies']
        return redirect(url_for('onboarding_goal'))
    return render_template('onboarding/allergies.html')

@app.route('/onboarding/goal', methods=['GET', 'POST'])
def onboarding_goal():
    if request.method == 'POST':
        session['goal'] = request.form['goal']
        return redirect(url_for('onboarding_muscle_gain'))
    return render_template('onboarding/goal.html')

@app.route('/onboarding/muscle_gain', methods=['GET', 'POST'])
def onboarding_muscle_gain():
    if request.method == 'POST':
        session['muscle_gain'] = request.form['muscle_gain']
        return redirect(url_for('onboarding_activity'))
    return render_template('onboarding/muscle_gain.html')

@app.route('/onboarding/activity', methods=['GET', 'POST'])
def onboarding_activity():
    if request.method == 'POST':
        session['activity'] = request.form['activity']
        return redirect(url_for('onboarding_timeline'))
    return render_template('onboarding/activity.html')

@app.route('/onboarding/timeline', methods=['GET', 'POST'])
def onboarding_timeline():
    if request.method == 'POST':
        session['timeline'] = request.form['timeline']
        return redirect(url_for('onboarding_diet'))
    return render_template('onboarding/timeline.html')

@app.route('/onboarding/diet', methods=['GET', 'POST'])
def onboarding_diet():
    if request.method == 'POST':
        if 'user_email' not in session:
            flash('Session expired. Please log in again.')
            return redirect(url_for('login'))
        
        # Get all session data
        user_email = session.get('user_email')
        gender = session.get('gender')
        age = session.get('age')
        weight = session.get('weight')
        height = session.get('height')
        skill = session.get('skill')
        allergies = session.get('allergies')
        goal = session.get('goal')
        muscle_gain = session.get('muscle_gain')
        activity = session.get('activity')
        timeline = session.get('timeline')
        diet = request.form.get('diet')
        
        # Save all onboarding data to MySQL
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            INSERT INTO onboarding (
                user_email, gender, age, weight, height, skill, allergies,
                goal, muscle_gain, activity, timeline, diet
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            user_email, gender, age, weight, height, skill, allergies,
            goal, muscle_gain, activity, timeline, diet
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Clear session data after saving to database
        session.pop('gender', None)
        session.pop('age', None)
        session.pop('weight', None)
        session.pop('height', None)
        session.pop('skill', None)
        session.pop('allergies', None)
        session.pop('goal', None)
        session.pop('muscle_gain', None)
        session.pop('activity', None)
        session.pop('timeline', None)
        session.pop('diet', None)
        
        return redirect(url_for('plan_summary'))
    
    return render_template('onboarding/diet.html')


# ---------------------------
# 3️⃣ PLAN SUMMARY PAGE
# ---------------------------

@app.route("/plan_summary")
def plan_summary():
    if "user_email" not in session:
        return redirect(url_for("login"))

    summary = {
        "gender": session.get("gender"),
        "age": session.get("age"),
        "height": session.get("height"),
        "weight": session.get("weight"),
        "skill": session.get("skill"),
        "allergies": session.get("allergies"),
        "goal": session.get("goal"),
        "muscle_gain": session.get("muscle_gain"),
        "activity": session.get("activity"),
        "timeline": session.get("timeline"),
        "diet": session.get("diet")
    }

    return render_template("plan_summary.html", summary=summary)


# ---------------------------
# 4️⃣ OTHER STATIC PAGES
# ---------------------------

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/home")
def home():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")



# ---------------------------
# 5️⃣ LOGOUT
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


from flask import render_template, request
from Foodimg2Ing import app
from Foodimg2Ing.utils.generate_recipe import generate_recipe

@app.route("/meal_plan_chef", methods=["GET", "POST"])
def meal_plan_chef():
    summary = None
    plan_recipes = []

    if request.method == "POST":
        # Collect form inputs
        gender = request.form.get("gender", "male")
        age = request.form.get("age", 21)
        height = request.form.get("height", 170)
        weight = request.form.get("weight", 70)
        goal = request.form.get("goal", "Eat Healthy")
        activity = request.form.get("activity", "Moderately Active")
        diet = request.form.get("diet", "None")
        days = int(request.form.get("duration_days", 3))

        # Calculate basic nutritional info (you can enhance this)
        bmr = 10 * float(weight) + 6.25 * float(height) - 5 * float(age)
        if gender == "male":
            bmr += 5
        else:
            bmr -= 161
        
        # Adjust for activity level
        activity_multipliers = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Active": 1.725,
            "Very Active": 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity, 1.55)
        
        # Adjust for goal
        if goal.lower() == "lose weight":
            calories = tdee * 0.8
        elif goal.lower() == "build muscle":
            calories = tdee * 1.1
        else:  # eat healthy
            calories = tdee

        summary = {
            "gender": gender,
            "age": age,
            "height": height,
            "weight": weight,
            "goal": goal,
            "activity": activity,
            "diet": diet,
            "days": days,
            "calories": int(calories),
            "protein": int((calories * 0.3) / 4),  # 30% from protein
            "carbs": int((calories * 0.4) / 4),    # 40% from carbs
            "fats": int((calories * 0.3) / 9)      # 30% from fats
        }

        base_prompt = f"""
        Create a healthy, unique recipe for a {age}-year-old {gender}.
        Nutritional targets: {int(calories)} calories, {summary['protein']}g protein, {summary['carbs']}g carbs, {summary['fats']}g fats.
        Goal: {goal}, Activity Level: {activity}, Diet Preference: {diet}.
        Use only whole foods; no packaged mixes.
        Make the recipe creative, delicious, and nutritionally balanced.
        """

        # Generate recipes for each day
        for day in range(1, days + 1):
            day_prompt = base_prompt + f"\nThis is for Day {day} and should be different from previous days."
            recipe = generate_recipe(day_prompt)
            
            plan_recipes.append({
                "day": day,
                "title": recipe.get("title", f"Day {day} Recipe"),
                "ingredients": recipe.get("ingredients", []),
                "directions": recipe.get("directions", [])
            })

    return render_template("meal_plan_chef.html", summary=summary, plan_recipes=plan_recipes)

from flask import render_template, request
from Foodimg2Ing.utils.generate_recipe import generate_recipe  # fixed import

@app.route('/pantry-chef', methods=['GET', 'POST'])
def pantry_chef():
    recipe = None
    if request.method == 'POST':
        meal_type = request.form.get('meal_type', '')
        cooking_time = request.form.get('cooking_time', '')
        ingredients = request.form.get('ingredients', '')

        # Build prompt for Gemini
        prompt = (
            f"Create a detailed recipe for {meal_type} "
            f"that takes about {cooking_time} minutes to cook. "
            f"Ingredients available: {ingredients}. "
            f"Provide a title, ingredients list with quantities, "
            f"and step-by-step cooking directions."
        )

        recipe = generate_recipe(prompt)

    return render_template('pantry_chef.html', recipe=recipe)


@app.route('/master-chef', methods=['GET', 'POST'])
def master_chef():
    recipe = None
    if request.method == 'POST':
        custom_input = request.form.get('custom_input', '')
        
        # Build prompt for the recipe model
        prompt = (
            f"Create a detailed recipe based on these preferences: {custom_input}. "
            "Provide a recipe title, ingredients list with quantities, "
            "and step-by-step cooking directions."
        )
        
        recipe = generate_recipe(prompt)
    
    return render_template('master_chef.html', recipe=recipe)


@app.route('/macros_chef', methods=['GET', 'POST'])
def macros_chef():
    recipe = None
    macros = None

    if request.method == 'POST':
        carbs = request.form.get('carbs')
        proteins = request.form.get('proteins')
        fats = request.form.get('fats')
        calories_input = request.form.get('calories')
        meal_type = request.form.get('meal_type')
        diet = request.form.get('diet')

        # Convert safely to float
        def to_float(x, default_val=0.0):
            try:
                return float(x)
            except Exception:
                return default_val

        carbs_val = to_float(carbs)
        proteins_val = to_float(proteins)
        fats_val = to_float(fats)
        calories_val = to_float(calories_input)

        # If any macro missing but calories provided → derive using default split (40/30/30)
        if (not carbs_val or not proteins_val or not fats_val) and calories_val > 0:
            from Foodimg2Ing.utils.nutrition import calculate_macros
            c, p, f = calculate_macros(calories_val)
            carbs_val = carbs_val or c
            proteins_val = proteins_val or p
            fats_val = fats_val or f

        # If calories missing → compute from macros
        if calories_val == 0:
            calories_val = round(carbs_val * 4 + proteins_val * 4 + fats_val * 9, 2)

        # ---- Build prompt for Gemini ----
        prompt = (
            f"Create a {meal_type.lower()} recipe that matches these macronutrient goals: "
            f"{int(carbs_val)}g carbohydrates, {int(proteins_val)}g protein, {int(fats_val)}g fats "
            f"(approximately {int(calories_val)} kcal). "
            f"The recipe should be {diet.lower()} friendly. "
            f"Include a clear title, a well-formatted list of ingredients with quantities, "
            f"and step-by-step cooking instructions."
        )

        # ---- Generate recipe using Gemini ----
        from Foodimg2Ing.utils.generate_recipe import generate_recipe
        recipe = generate_recipe(prompt)

        # ---- Prepare macro summary ----
        macros = {
            'carbs': str(int(carbs_val)),
            'proteins': str(int(proteins_val)),
            'fats': str(int(fats_val)),
            'calories': int(calories_val),
            'meal_type': meal_type,
            'diet': diet
        }

    else:
        macros = {
            'carbs': '',
            'proteins': '',
            'fats': '',
            'calories': '',
            'meal_type': '',
            'diet': ''
        }

    return render_template('macros_chef.html', recipe=recipe, macros=macros)


@app.route('/photo_chef', methods=['GET', 'POST'])
def photo_chef():
    uploaded_image = None
    recipe_list_to_return = []

    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            upload_path = os.path.join('static', 'uploads', file.filename)
            file.save(upload_path)
            uploaded_image = base64.b64encode(file.read()).decode('ascii')

            # Get structured recipes
            recipe_list_to_return = generate_recipe_from_image(upload_path)

    return render_template(
        'photo_chef.html',
        uploaded_image=uploaded_image,
        recipe_list_to_return=recipe_list_to_return[:4],
        similar_recipe_list=recipe_list_to_return[4:10]
    )



