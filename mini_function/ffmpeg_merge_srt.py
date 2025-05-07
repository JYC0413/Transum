import subprocess


def ffmpeg_merge_srt(srt_file, video_file, output_folder):
    video_file_path = f"{output_folder}/{video_file}"
    output_video_file_path = f"{output_folder}/hard_output_{video_file}"

    # 使用 ffmpeg 合并视频和字幕
    command = [
        'ffmpeg',
        "-y",
        '-i', video_file_path,
        '-vf', f'subtitles={srt_file}:force_style="Alignment=10"',
        output_video_file_path
    ]
    # ffmpeg -i video.mp4 -vf subtitles=subtitle.srt output.mp4

    try:
        subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"Successfully merged {video_file} and {srt_file} into hard_output_{video_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging {video_file} and {srt_file}: {e}")
