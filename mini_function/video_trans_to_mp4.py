import os
import subprocess


def video_trans_to_mp4(filename, save_folder):
    file_path = os.path.join(save_folder, filename)
    if not filename.lower().endswith('.mp4'):
        base_name = os.path.splitext(filename)[0]
        mp4_file = base_name + '.mp4'
        mp4_path = os.path.join(save_folder, mp4_file)
        ffmpeg_command = [
            'ffmpeg',
            '-i', file_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            mp4_path
        ]
        try:
            subprocess.run(ffmpeg_command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            os.remove(file_path)
            return mp4_file
        except subprocess.CalledProcessError as e:
            print(f"转换 {filename} 为 mp4 时出错：{e}")
            return None
    else:
        return filename


if __name__ == "__main__":
    video_trans_to_mp4("example/example_en_video.mkv", "")
    print("Conversion complete")
