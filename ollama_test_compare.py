import ollama
import base64
import os
import subprocess
import json

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# prompt="""
#     Does this screen shot from the *Siskel & Ebert* show match this description: "A review graphic with the possible name a of a Movie, a movie rating, and the text 'Gene' or 'Roger' and likly 'YES' or 'NO'".
#     If the name of the movie is visible, include it in the response.
#     Responsed in ONLY VALID JSON in the format: { "is_review_graphic": true/false, "movie_name": "<movie_name>", "reasoning": "one sentence explanation of why it is or isn't a review graphic" }.
# """

# # prompt="""Describe this still from the *Siskel & Ebert* show."""

# client = ollama.Client(
#     host='http://192.168.1.60:11434',
#     headers={'x-some-header': 'some-value'},
#     timeout=60
# )
# response = client.chat(
#     # model="qwen2.5vl:32b",
#     model="qwen2.5vl:7b",
#     # temperature=0,
#     messages=[
#         {
#             "role": "user",
#             "content": prompt,
#             "images": [encode_image("sneak_previews_example.png")],
#         }
#     ],
# )

# print(response['message']['content'])


# xxxxxxxx=x




VIDEO_DIR = '/Volumes/NextGlum/s_and_e/'

def format_time(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"


TEST_IMAGE_SE_DISNEY = encode_image("se_disney_example.png")


movies = json.load(open('final_data.json', 'r'))
titles_lookup = {}
done_video_ids = []
for movie in movies:
    if movie['video_id'] not in titles_lookup:
        titles_lookup[movie['video_id']] = [movie['title']]
    else:
        titles_lookup[movie['video_id']].append(movie['title'])
        

print(len(titles_lookup))    

for movie in movies:

    if movie['video_id'] in done_video_ids:
        continue

    if os.path.exists('/Volumes/NextGlum/s_and_e_find_card_alt/' + movie['video_id'] + '.json'):

        results = json.load(open('/Volumes/NextGlum/s_and_e_find_card_alt/' + movie['video_id'] + '.json', 'r'))
        found_possible_review_graphic = False
        for r in results:
            if 'response' in r:
                if r['response']['is_review_graphic'] == True:
                    # print("Already found review graphic for " + movie['video_id'] + ' ' + movie['title'])

                    found_possible_review_graphic = True

        if found_possible_review_graphic != True:
            # print("Did not find review graphic for " + movie['video_id'] + ' ' + movie['title'] + ', reprocessing.')
            pass
        else:
            continue

    # print(movie["show"].lower().replace(' ',''))

    if movie["show"].lower().replace(' ','') ==  'openingsoon':#'':#'sneakpreviews': #'atmtribune': # "erdisney": #"SE Disney"
        # print("Skipping " + movie["show"] + ".")
        continue
    
    if 'video_id_alt' not in movie:
        # print("No alt video ID for " + movie['video_id'] + ' ' + movie['title'])
        continue

    print("need to  do: " + movie['video_id'] + ' ' + movie['title'], len(movie['video_id_alt']))
    
    movie['video_id'] = movie['video_id_alt'][0]
    
    print("need to  do: " + movie['video_id'] + ' ' + movie['title'])



    video_path = VIDEO_DIR + movie['video_id'] + '.mp4'

    # get the length of video
    command = [
        "ffprobe",
        "-i", video_path,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "csv=p=0"
    ]
    length = subprocess.run(command, check=True, capture_output=True, text=True)
    length = length.stdout.strip()
    # hours, minutes, seconds = length.split(':')    
    # print(length)
    length = int(float(length))  # Convert to float for easier manipulation

    min = 5
    if length < 500 and length > 60:
        # print(length, movie['video_id'] + '.mp4')
        min = 3
    elif length < 1000 and length > 60:
        # print(length, movie['video_id'] + '.mp4')
        min = 4

    # elif length > 1200:
    else:
        # print(length, movie['video_id'] + '.mp4')
        min = 6




    print(length)
    results = []
    for current_time in range(length, length - (min*60), -2):
        print( format_time(current_time), " | ", current_time)

        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-ss", str(current_time),
            "-i", video_path,
            "-vframes", "1",
            "tmp.png"
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        encoded_image = encode_image("tmp.png")

        # prompt = """You are comparing two images. The first is an example of the title review card for the show *Siskel & Ebert*.
        # The second is a frame from the same show that may or may not be a title review card.
        # Use the first image as a reference for what a title review card looks like, the movie name and other details will be different.
        # Compare the two images and return a JSON object with the following fields:
        # {
        #     "is_review_graphic": true/false,
        #     "reasoning": "one sentence explanation of why it is or isn't a review graphic"
        # }
        # Set is_review_graphic to true if the second image is a title review card, false otherwise.
        # """
        # THE DISNEY PRPOMPT
        # prompt="""
        #     Does this screen shot from the *Siskel & Ebert* show match this description: "A film strip graphic with a thumbs-up or thumbs-down icon(s) and text that could be a movie name".
        #     If the name of the movie is visible, include it in the response.
        #     Responsed in ONLY VALID JSON in the format: { "is_review_graphic": true/false, "movie_name": "<movie_name>", "reasoning": "one sentence explanation of why it is or isn't a review graphic" }.
        # """

        # THE AMT TRIBUNE PROMPT
        prompt="""
            Does this screen shot from the *Siskel & Ebert* show match this description: "A review graphic with a thumbs-up or thumbs-down silhouette, the text that could be a movie name, a possible still from the a movie, and the text 'Gene' or 'Roger'".
            "R" or "PG" or "G" or "PG-13" or "X" or "NC-17" are not movie names, they are ratings.
            If the name of the movie is visible, include it in the response.
            Responsed in ONLY VALID JSON in the format: { "is_review_graphic": true/false, "movie_name": "<movie_name>", "reasoning": "one sentence explanation of why it is or isn't a review graphic" }.
        """

        client = ollama.Client(
            host='http://192.168.1.60:11434',
            headers={'x-some-header': 'some-value'},
            timeout=60
        )

        try:
            response = client.chat(
                # model="qwen2.5vl:32b",
                model="qwen2.5vl:7b",
                # temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [encoded_image],
                    }
                ],
            )
        except:
            print("Error with Ollama chat request, skipping this image.")
            continue

        try:

            response['message']['content'] = response['message']['content'].replace('```json', '').replace('```', '').strip()
            


            response_json = json.loads(response['message']['content'])
            results.append({
                "video_id": movie['video_id'],
                "timestamp": current_time,
                "format_time": format_time(current_time),
                "response": response_json
            })
            print(current_time, response_json)

            json.dump(results, open('/Volumes/NextGlum/s_and_e_find_card_alt/' + movie['video_id'] + '.json', 'w'), indent=4)

        except json.JSONDecodeError:
            print("JSONDecodeError:", response['message']['content'])
            results.append({'ERROR': 'JSONDecodeError', 'video_id': movie['video_id'], 'timestamp': current_time})
            json.dump(results, open('/Volumes/NextGlum/s_and_e_find_card_alt/' + movie['video_id'] + '.json', 'w'), indent=4)
            continue



        # do ssssssss

        prompt="""
            Does this screen shot from the *Siskel & Ebert* show match this description: "A film strip graphic with a thumbs-up or thumbs-down icon(s) and text that could be a movie name".
            If the name of the movie is visible, include it in the response.
            Responsed in ONLY VALID JSON in the format: { "is_review_graphic": true/false, "movie_name": "<movie_name>", "reasoning": "one sentence explanation of why it is or isn't a review graphic" }.
        """

        client = ollama.Client(
            host='http://192.168.1.60:11434',
            headers={'x-some-header': 'some-value'},
            timeout=60
        )

        try:
            response = client.chat(
                # model="qwen2.5vl:32b",
                model="qwen2.5vl:7b",
                # temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [encoded_image],
                    }
                ],
            )
        except:
            print("Error with Ollama chat request, skipping this image.")
            continue

        try:

            response['message']['content'] = response['message']['content'].replace('```json', '').replace('```', '').strip()
            


            response_json = json.loads(response['message']['content'])
            results.append({
                "video_id": movie['video_id'],
                "timestamp": current_time,
                "format_time": format_time(current_time),
                "response": response_json
            })
            print(current_time, response_json)

            json.dump(results, open('/Volumes/NextGlum/s_and_e_find_card_alt/' + movie['video_id'] + '.json', 'w'), indent=4)

        except json.JSONDecodeError:
            print("JSONDecodeError:", response['message']['content'])
            results.append({'ERROR': 'JSONDecodeError', 'video_id': movie['video_id'], 'timestamp': current_time})
            json.dump(results, open('/Volumes/NextGlum/s_and_e_find_card_alt/' + movie['video_id'] + '.json', 'w'), indent=4)
            continue



        prompt="""
            Does this screen shot from the *Siskel & Ebert* show match this description: "A review graphic with the possible name a of a Movie, a movie rating, and the text 'Gene' or 'Roger' and likly 'YES' or 'NO'".
            If the name of the movie is visible, include it in the response.
            Responsed in ONLY VALID JSON in the format: { "is_review_graphic": true/false, "movie_name": "<movie_name>", "reasoning": "one sentence explanation of why it is or isn't a review graphic" }.
        """

        client = ollama.Client(
            host='http://192.168.1.60:11434',
            headers={'x-some-header': 'some-value'},
            timeout=60
        )

        try:
            response = client.chat(
                # model="qwen2.5vl:32b",
                model="qwen2.5vl:7b",
                # temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [encoded_image],
                    }
                ],
            )
        except:
            print("Error with Ollama chat request, skipping this image.")
            continue

        try:

            response['message']['content'] = response['message']['content'].replace('```json', '').replace('```', '').strip()
            


            response_json = json.loads(response['message']['content'])
            results.append({
                "video_id": movie['video_id'],
                "timestamp": current_time,
                "format_time": format_time(current_time),
                "response": response_json
            })
            print(current_time, response_json)

            json.dump(results, open('/Volumes/NextGlum/s_and_e_find_card_alt/' + movie['video_id'] + '.json', 'w'), indent=4)

        except json.JSONDecodeError:
            print("JSONDecodeError:", response['message']['content'])
            results.append({'ERROR': 'JSONDecodeError', 'video_id': movie['video_id'], 'timestamp': current_time})
            json.dump(results, open('/Volumes/NextGlum/s_and_e_find_card_alt/' + movie['video_id'] + '.json', 'w'), indent=4)
            continue














    done_video_ids.append(movie['video_id'])
