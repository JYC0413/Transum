import os
import subprocess


def get_thumbnail(filename, save_folder):
    file_name = os.path.splitext(filename)[0]
    thumbnail_path = os.path.join(save_folder, f"temp_{file_name}.jpg")
    filepath = os.path.join(save_folder, filename)
    subprocess.run([
        'ffmpeg',
        '-i', filepath,
        '-ss', "00:00:01",
        '-vframes', '1',
        '-q:v', '2',
        thumbnail_path
    ], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return thumbnail_path


if __name__ == "__main__":
    # Example usage
    thumbnail_path = get_thumbnail("example_en_audio.wav", "")
    print(f"Thumbnail saved to {thumbnail_path}")

