import openai
import requests

HA_URL = "<your Home Assistant URL>"
HAKEY = "<your Home Assistant long lived access token>"
OPENAIKEY = "<your OpenAI API key>"

tbd_placeholder_text = "TBD"
titles = ["Braised Duck Leg With Roasted Turnips Over Gigante Bean Purée, Molé Chicken Quesadillas, Chili Turkey Dogs, Ravioli, Chicken & Protein Waffles, Carrot Apple Soup With Cheesy Toast, Tortilla Pizzas, Turkey Burgers With Roasted Sprouts, Pollo a La Plancha Con Charro Beans, Veggie & Hummus Platter, Surf or Turf With Roasted Broccoli, Bagel Thin Sandwiches, Salads & Minestrone Soup, Firecracker Chicken Meatball Lettuce Boats, Sweet Potato Shepherds Pie & Steamed Artichoke, Bourbon Chkn & Smashed Cucumber Salad, Chili Over Quest Chips, Air Fryer Chicken Pepperoni, Broccoli & Cheese Baked Potato, Spanish Onion Soup, Tofu Veggie Soup, Red Beans & Rice, Turkey Wraps, Cabbage & Italian Meatball Soup, Sesame Crunch Salad with Grilled Chicken, Cucumber Sandwiches, Bbq Chk Skewers with Smashed Sprouts, Bourbon Chicken, Bahn Mi Style Salad, Cheesesteak Salad, Veggie Quesadillas , Chicken & Spinach Skillet Pasta with Lemon & Parmesean, Steak & Onion Sandwich on Keto Bun, Apple Bacon & Sweet Potato Mini Casseroles, Spicy Potato Tacos, Carrot Soup With Cheesy Toast Points, Avocado Toast, Air Fried Apple on Peanut Butter Toast, Chicken Meatball and Marina Subs, Turkey Apple Cheddar Sandwich, Strawberry-Ricotta Waffle Sandwich, Caprese & Prosciutto Bagel Thin Sandwich, Tortilla Pizza Roll-up, Gyoza W Spicy Snow Peas & Water Chestnuts, Mozzarella, Basil & Zucchini Frittata, Katie’s Pasta Salad With Low Oil, Butternut Squash Ravioli, Air Fryer Sweet Potato Chip Chicken Nachos, Chk & Cuke Lettuce Wraps with Peanut Sauce, Turkey Bacon Cheddar Lettuce Wraps, Air Fried Chicken Tenders with Honey Mustard, Grilled Thai Coconut Chicken Skewers, Ginger Salad & Egg Drop Soup With Tofu, Poblano Enchiladas, Veggie and Gnocchi Soup, Loaded Baked Potato, Phyllo Pot Pie, Phyllo Calzone, Phyllo & Brie With Marinara Dipping Sauce, Cheeseburger Wonton Cups, Pizza Wonton Cups, Bagel Pizzas, Buffalo Stuffed Peppers, Turkey Burgers, Chili Topped Sweet Potatoes, Wings, Sandwiches, Movie & Yerro Village, Sushi, Pot Roast Over Mashed Parsnips, Turkey Dogs, Chicken Tortilla Soup, Brie & Apple Panini, Buffalo Chicken Salad, Chicken Burrito Bowls, Spinach & Strawberry Salad W Goat Cheese, Zucchini & Couscous Pizza Boats, Roast Veggies and Tortellini, Turkey Bacon & Pistachio Chopped Salad"]
num_similar_titles = 14

# Preprocess titles
formatted_titles = "\n".join(titles)
prompt = f"Given the following recipe titles, generate {num_similar_titles} similar recipe titles:\n{formatted_titles}. Recipes should be low calorie and should not contain seafood.\n"

name_entity_ids = [
    'input_text.monday_lunch',
    'input_text.tuesday_lunch',
    'input_text.wednesday_lunch',
    'input_text.thursday_lunch',
    'input_text.friday_lunch',
    'input_text.saturday_lunch',
    'input_text.sunday_lunch',
    'input_text.monday_dinner',
    'input_text.tuesday_dinner',
    'input_text.wednesday_dinner',
    'input_text.thursday_dinner',
    'input_text.friday_dinner',
    'input_text.saturday_dinner',
    'input_text.sunday_dinner'
]

headers = {
    "Authorization": f"Bearer {HAKEY}",
    "Content-Type": "application/json",
}


# Call OpenAI API
openai.api_key = OPENAIKEY
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.7,
)
response_text = response.choices[0].text.strip()

# Extract similar titles
recipe_titles = [title.strip() for title in response_text.split(",")]

for index, entity_id in enumerate(name_entity_ids):
    print(f"Processing {entity_id} at index {index}.")
    print(f"{recipe_titles[index]}")

    url = f"{HA_URL}/api/states/{entity_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        entity_state = response.json()["state"]
        if entity_state == tbd_placeholder_text or entity_state == "":
            url = f"{HA_URL}/api/states/{entity_id}"
            payload = { "state": f"{recipe_titles[index]}"}
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"Setting state for {entity_id}")
    else:
        print(f"Error getting state for {entity_id}")
        continue