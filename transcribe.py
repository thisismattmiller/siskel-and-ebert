import glob
import os
import subprocess
import json

def transcribe_audio(input_dir, output_dir):
    """
    Loops through all MP4 files in the input directory, converts them to WAV
    if a corresponding JSON file doesn't exist in the output directory,
    and saves the WAV file.
    """
    for mp4_file in glob.glob(os.path.join(input_dir, "*.mp4")):
        mp4_filename = os.path.basename(mp4_file)
        mp4_name_without_extension = os.path.splitext(mp4_filename)[0]
        json_file = os.path.join(output_dir, f"{mp4_name_without_extension}.json")
        wav_file = os.path.join(output_dir, f"{mp4_name_without_extension}.wav")

        if not os.path.exists(json_file):
            print(f"Converting {mp4_file} to {wav_file}")
            command = f"ffmpeg -y -i {mp4_file} -ar 16000 -ac 1 -c:a pcm_s16le {wav_file}"
            print(command)
            subprocess.call(command, shell=True)
        else:
            print(f"JSON file already exists for {mp4_filename}, skipping conversion.")
            continue

        command = f"/Users/m/git/whisper.cpp/build/bin/whisper-cli -m /Users/m/git/whisper.cpp/models/ggml-medium.en.bin -f {wav_file} --output-json --output-txt --output-srt --output-vtt --output-file /Volumes/NextGlum/s_and_e_text/{mp4_name_without_extension}"
        subprocess.call(command, shell=True)
        os.remove(wav_file)
        # break
if __name__ == "__main__":
    input_directory = "/Volumes/NextGlum/s_and_e/"
    output_directory = "/Volumes/NextGlum/s_and_e_text/"
    transcribe_audio(input_directory, output_directory)