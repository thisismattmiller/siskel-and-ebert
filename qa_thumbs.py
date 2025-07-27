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


results = {}# json.load(open('thumbs_results.json', 'r'))
VIDEO_DIR = '/Volumes/NextGlum/s_and_e/'


PAIRED_IMAGES_DIR = "/Volumes/NextGlum/s_and_e_paired_images"

for filename in os.listdir(PAIRED_IMAGES_DIR):
    if filename.lower().endswith(".png"):

        if filename in results:
            print(f"Skipping {filename} as it has already been processed.")
            continue
        full_path = os.path.join(PAIRED_IMAGES_DIR, filename)
       
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
                    types.Part.from_text(text="""This is a screen shot from the TV Show Siskel and Ebert, is a Thumbs up or Thumbs Down clearly visible? If they are transparent/see through they are not clearly visible.  Return as JSON: {\"thumbs_visible\":true/false}
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
            results[filename] = data
            json.dump(results, open('thumbs_results.json', 'w'), indent=4)
            print(data)
        except json.JSONDecodeError:
            print(f"Could not parse json from: {chunk.text}")






