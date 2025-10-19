def calculate_bmr(gender, weight, height, age):
    if gender == 'male':
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    return bmr * activity_factors.get(activity_level, 1.2)

def adjust_for_goal(tdee, goal):
    if goal == 'weight_loss':
        return tdee - 500
    elif goal == 'muscle_gain':
        return tdee + 300
    return tdee

def calculate_macros(calories):
    carbs = (0.4 * calories) / 4
    protein = (0.3 * calories) / 4
    fats = (0.3 * calories) / 9
    return round(carbs), round(protein), round(fats)
