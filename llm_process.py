# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types
import glob
import json

def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    for file in glob.glob("/Volumes/NextGlum/s_and_e_text/*.vtt"):

        file_id = os.path.basename(file).replace('.vtt', '')

        if os.path.exists(f"/Volumes/NextGlum/s_and_e_llm/{file_id}.json"):
            print(f"Skipping {file} as it has already been processed.")
            continue

        with open(file, "r") as f:
            text = f.read()
            
            model = "gemini-2.5-flash-preview-05-20"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=text),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "movies_reviewed": genai.types.Schema(
                            type = genai.types.Type.ARRAY,
                            items = genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                properties = {
                                    "title": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "director": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                        nullable = "True",
                                    ),
                                    "discussion_start_timestamp": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "recap_start_timestamp": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "siskel_opinion": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                        enum = ["Liked", "Disliked", "N/A"],
                                    ),
                                    "ebert_opinion": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                        enum = ["Liked", "Disliked", "N/A"],
                                    ),
                                },
                            ),
                        ),
                        "final_summary_timestamp": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "named_entities": genai.types.Schema(
                            type = genai.types.Type.ARRAY,
                            items = genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                properties = {
                                    "name": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "type": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "timestamps": genai.types.Schema(
                                        type = genai.types.Type.ARRAY,
                                        items = genai.types.Schema(
                                            type = genai.types.Type.STRING,
                                        ),
                                    ),
                                },
                            ),
                        ),
                    },
                ),
                system_instruction=[
                    types.Part.from_text(text="""You are a helpful assistant extracting information from Siskel & Ebert movie review television show transcripts in VTT format. Respond in JSON format return what movies and their director they talk about and the time stamps for when they begin in-depth discussion for each movie and the timestamp that the recap their review of the movie at the end of the episode. Also return a timestamp when they start to review all of the movies at the end of the show. For their final summary for each movie return if Siskel & Ebert liked or disliked the movie.   Also perform named entity recognition on the text with the name of the entity, the type of the entity and the timestamps they were mentioned. """),
                ],
            )
            response_text = ''
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                print(chunk.text, end="")
                if chunk.text is None:
                    continue
                response_text += chunk.text

            # try:
                # response_json = genai.types.JsonValue.from_json(response_text)
                # print("\n\nResponse JSON:", response_json.to_dict())
            
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
                print(f"Response text: {response_text}")
                continue

            print("\n\nResponse JSON:", data)
            json.dump(data, open(f"/Volumes/NextGlum/s_and_e_llm/{file_id}.json", "w"), indent=4)

if __name__ == "__main__":
    generate()
