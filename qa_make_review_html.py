import json
import base64
import os
import hashlib

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")




review_data = json.load(open('final_qa_results.json', 'r'))

data = json.load(open('final_data.json', 'r'))

bad_matches = []

for movie in data:

    title_hash = hashlib.md5(movie['title'].encode('utf-8')).hexdigest()
    movie_id = movie['video_id'] + '_' + title_hash

    image = False
    movie['movie_id'] = movie_id
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
        # print(f"No image found for {movie['title']} ({movie['video_id']})")
        continue

    if movie_id in review_data:


    
        
    # VIDEO_DIR = '/Volumes/NextGlum/s_and_e/'
        if review_data[movie_id]['is_review_graphic'] == False:
                


            PAIRED_IMAGES_DIR = "/Volumes/NextGlum/s_and_e_paired_images_good"
            
            full_path = os.path.join(PAIRED_IMAGES_DIR, image)

            movie['image'] = full_path
            movie['image_base64'] = encode_image(full_path)


            bad_matches.append(movie)



html = "<html><head><title>Bad Matches</title></head><body>"
html += "<table border=1>"
html += "<tr><th>Title</th><th>Image</th></tr>"

for movie in bad_matches:
    html += "<tr>"
    html += f"<td>{movie['title']}</td>"
    html += f"<td>{movie['video_id']}</td>"

    html += f"<td>{movie['movie_id']}</td>"
    html += f"<td><img src='data:image/png;base64,{movie['image_base64']}' width='500'></td>"
    html += "</tr>"

html += "</table>"
html += "</body></html>"

with open('bad_matches.html', 'w') as f:
    f.write(html)