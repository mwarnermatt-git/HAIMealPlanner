import openai
import requests
import os
from PIL import Image, ImageDraw, ImageFont
import io

HA_URL = "<your Home Assistant URL>"
YOUTUBE_URL = 'https://www.googleapis.com/youtube/v3/search'
HAKEY = "<your Home Assistant long lived access token>"
OPENAIKEY = "<your OpenAI API key>"
YOUTUBEKEY = "<your YouTube API key>" 
IMAGEPROMPT = ", professional food photography"
TEXTPROMPT = "Write a recipe having two servings with ingredients, instructions, calories and no title for a recipe for "
openai.api_key = OPENAIKEY #os.getenv("OPENAI_API_KEY")

# Define the entity IDs
url_entity_ids = [
    'input_text.monday_lunch_url',
    'input_text.tuesday_lunch_url',
    'input_text.wednesday_lunch_url',
    'input_text.thursday_lunch_url',
    'input_text.friday_lunch_url',
    'input_text.saturday_lunch_url',
    'input_text.sunday_lunch_url',
    'input_text.monday_dinner_url',
    'input_text.tuesday_dinner_url',
    'input_text.wednesday_dinner_url',
    'input_text.thursday_dinner_url',
    'input_text.friday_dinner_url',
    'input_text.saturday_dinner_url',
    'input_text.sunday_dinner_url'
]

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

recipe_entity_ids = [
    'sensor.monday_lunch_recipe',
    'sensor.tuesday_lunch_recipe',
    'sensor.wednesday_lunch_recipe',
    'sensor.thursday_lunch_recipe',
    'sensor.friday_lunch_recipe',
    'sensor.saturday_lunch_recipe',
    'sensor.sunday_lunch_recipe',
    'sensor.monday_dinner_recipe',
    'sensor.tuesday_dinner_recipe',
    'sensor.wednesday_dinner_recipe',
    'sensor.thursday_dinner_recipe',
    'sensor.friday_dinner_recipe',
    'sensor.saturday_dinner_recipe',
    'sensor.sunday_dinner_recipe'
]



headers = {
    "Authorization": f"Bearer {HAKEY}",
    "Content-Type": "application/json",
}

for index, entity_id in enumerate(name_entity_ids):
    print(f"Processing {entity_id} at index {index}.")

    url = f"{HA_URL}/api/states/{entity_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        entity_state = response.json()["state"]
    else:
        print(f"Error getting state for {entity_id}")
        continue

    filename = f"{entity_id}".split('.')[1] + ".jpg"
    local_path = os.path.join(os.getcwd(), "www", "images", filename)
    import os
    font_file = "MutantHound-Free.ttf"
    font_path = os.path.join(os.getcwd(), "www", "fonts", font_file)
    

    if entity_state != "TBD":
        openairesponse = openai.Image.create(
            prompt=f"{entity_state} " + IMAGEPROMPT,
            n=1,
            size="512x512",
        )
        print(openairesponse["data"][0]["url"])
        image_url = openairesponse["data"][0]["url"]

        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            # Load the image from response content
            image = Image.open(io.BytesIO(response.content))

            # Customize the text and font properties
            font_size = 60
            font = ImageFont.truetype(font_path, font_size)
            text = f"{entity_state}"
            words = text.split()
            lines = []
            current_line = []
            max_chars_per_line = 18

            for word in words:
                if len(' '.join(current_line + [word])) <= max_chars_per_line:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]

            # Add the last line if it's not empty
            if current_line:
                lines.append(' '.join(current_line))

            draw = ImageDraw.Draw(image)
            text_width, text_height = draw.textsize(text, font=font)

            # Customize the position of the text
            line_spacing = 10
            total_text_height = (text_height * len(lines)) + (line_spacing * (len(lines) - 1))
            start_x = (image.width - text_width) // 2
            start_y = (image.height - total_text_height) // 2

            # Draw the black outline
            outline_width = 2
            for off_x in range(-outline_width, outline_width + 1):
                for off_y in range(-outline_width, outline_width + 1):
                    for i, line in enumerate(lines):
                        line_width, _ = draw.textsize(line, font=font)
                        line_x = (image.width - line_width) // 2
                        line_y = start_y + (text_height + line_spacing) * i
                        draw.text((line_x + off_x, line_y + off_y), line, font=font, fill="black")


            # Draw the text on the image (in the desired color)
            for i, line in enumerate(lines):
                line_width, _ = draw.textsize(line, font=font)
                line_x = (image.width - line_width) // 2
                line_y = start_y + (text_height + line_spacing) * i
                draw.text((line_x, line_y), line, font=font, fill="white")


            # Save the image with the overlay text
            image.save(local_path)
            print(f"Image saved to {local_path}")
        else:
            print("Failed to download image")

        #Call OpenAI to generate recipe text
        openairesponsetext = openai.Completion.create(
            model="text-davinci-003",
            prompt=TEXTPROMPT + f"{entity_state}.",
            temperature=0.3,
            max_tokens=400,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
            )
        print(openairesponsetext.choices[0].text)
        recipe_text = str(openairesponsetext.choices[0].text)

        #Update Home Assistant entity with recipe text
        url = f"{HA_URL}/api/states/{recipe_entity_ids[index]}"
        payload = {
            "state": "Available",
            "attributes": {
                "content": recipe_text,
            },
        }
        response = requests.post(url, json=payload, headers=headers)


        if response.status_code == 200:
            print(f"Recipe set for {recipe_entity_ids[index]}.")
        
        #Generate youtube playlist from recipe title
        params = {
            'part': 'snippet',
            'q': f"{entity_state} recipe",
            'type': 'video',
            'maxResults': 10,
            'key': YOUTUBEKEY,
        }

        response = requests.get(YOUTUBE_URL, params=params)
        data = response.json()

        try:
            video_id = data['items'][0]['id']['videoId']
            video_title = data['items'][0]['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"Video ID: {video_id}, Title: {video_title}, URL: {video_url}") 

            video_ids = []
            for item in data['items']:
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                print(f"Video ID: {video_id}, Title: {video_title}")
                video_ids.append(video_id)
            
            playlist_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"
        except IndexError:
            print("No results found.")

        #Set entity url as youtube playlist API call results
        url = f"{HA_URL}/api/states/{url_entity_ids[index]}"
        payload = { "state": playlist_url }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"URL set for {recipe_entity_ids[index]}.")