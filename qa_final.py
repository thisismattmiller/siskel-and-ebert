import json
import subprocess
import base64
import os
from google import genai
from google.genai import types


import io
from typing import Union
from google.cloud import vision
import hashlib
import shutil


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")



client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
)


data = json.load(open('final_data.json', 'r'))
results = json.load(open('final_qa_results.json', 'r')) if os.path.exists('final_qa_results.json') else {}


for movie in data:

    title_hash = hashlib.md5(movie['title'].encode('utf-8')).hexdigest()
    movie_id = movie['video_id'] + '_' + title_hash

    image = False
    
    if os.path.exists(f'/Volumes/NextGlum/s_and_e_paired_images_good/{movie_id}.png'):
        image = f'/Volumes/NextGlum/s_and_e_paired_images_good/{movie_id}.png'
    elif 'video_id_alt' in movie:
        if len(movie['video_id_alt']) > 0:


            movie_id = movie['video_id_alt'][0]  + '_' + title_hash


            if os.path.exists(f'/Volumes/NextGlum/s_and_e_paired_images_good/{movie_id}.png'):
                image = f'/Volumes/NextGlum/s_and_e_paired_images_good/{movie_id}.png'

    if image != False:

        # print(image)
        pass
    else:
        print(f"No image found for {movie['title']} ({movie['video_id']})")
        continue

    if movie_id in results:
        print(f"Skipping {movie_id} as it has already been processed.")
        continue
    
        
    # VIDEO_DIR = '/Volumes/NextGlum/s_and_e/'


    PAIRED_IMAGES_DIR = "/Volumes/NextGlum/s_and_e_paired_images_good"




    full_path = os.path.join(PAIRED_IMAGES_DIR, image)

    print(full_path)

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type="image/png",
                    data=encode_image(full_path),
                ),
                types.Part.from_text(text="""This is a screen shot from the TV Show Siskel and Ebert. Does it look like the final review graphic for the movie: """ + movie['title'] + """ with a rating and the title displayed? Return as JSON: {\"is_review_graphic\":true/false, "reasoning":"<reasoning for the answer>"}
                """),
            ],
        ),           
        
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        response_mime_type="application/json",
    )

    response = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.text != None:
            response += chunk.text

    try:
        data = json.loads(response)
        results[movie_id] = data
        json.dump(results, open('final_qa_results.json', 'w'), indent=4)
        print(data)
    except json.JSONDecodeError:
        print(f"Could not parse json from: {chunk.text}")






