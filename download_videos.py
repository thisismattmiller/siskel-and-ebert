import json
from subprocess import Popen, PIPE
import time

def download_videos():
    """Downloads videos using yt-dlp based on the configuration in by_video.json."""

    try:
        with open("by_video.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: by_video.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in by_video.json.")
        return

    for key, videos in data.items():
        print(videos['id'])
        if 'movies' in videos:
            video = videos['movies'][0]            
            print(f"Processing video: {key}")
            video_id = data[key].get('id')
            
            print(f"Video ID: {video_id}")

            if 'stdout' in data[key]:
                print(f"Video {video_id} already processed, skipping.")
                continue

            data[key]['stdout'] = ''

            with Popen(["yt-dlp", "-P", "/Volumes/NextGlum/s_and_e/", "-o", f"{video_id}.mp4", "-S", "vcodec:h264,res,acodec:m4a", '--recode', 'mp4', key], stdout=PIPE, bufsize=1, universal_newlines=True) as p:
                for line in p.stdout:
                    print(line, end='') # process line here
                    data[key]['stdout'] = data[key]['stdout'] + line  + '\n'
                
                data[key]['returncode'] = p.returncode
                    



            # data[key]['stdout'] = stdout.decode()
            # data[key]['stderr'] = stderr.decode()
            with open("by_video.json", "w") as f:
                json.dump(data, f, indent=4)

        print("Waiting for 60 seconds before the next download...")
        time.sleep(60)

if __name__ == "__main__":
    download_videos()