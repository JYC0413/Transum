import re
import os

export_folder = "srt_output"


def convert_milliseconds_to_time_format(milliseconds):
    # 计算小时
    hours = milliseconds // (60 * 60 * 1000)
    milliseconds %= (60 * 60 * 1000)

    # 计算分钟
    minutes = milliseconds // (60 * 1000)
    milliseconds %= (60 * 1000)

    # 计算秒
    seconds = milliseconds // 1000
    # 剩下的是毫秒
    milliseconds %= 1000

    # 格式化成 HH:MM:SS,xxx
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"


def convert_to_srt(input_text, video_file):
    pattern = r"\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]  (.+)"

    output_file = os.path.join(export_folder, os.path.splitext(os.path.basename(video_file))[0] + ".srt")

    with open(output_file, "w", encoding="utf-8") as f:
        matches = re.findall(pattern, input_text)
        for idx, (start_time, end_time, text) in enumerate(matches, 1):
            start_time = start_time.replace('.', ',')
            end_time = end_time.replace('.', ',')

            f.write(f"{idx}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

    with open(output_file, "r", encoding="utf-8") as f:
        return f.read()
