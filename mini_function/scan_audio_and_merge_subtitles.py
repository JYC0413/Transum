import re
import os
import redis
from mini_function.query_function import query_gaia_whisper
from datetime import datetime, timedelta
from rq import Queue


# Get Redis connection details from environment variables
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)

def get_redis_client():
    """Create and return a Redis client using environment variables"""
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD
    )
    return client


def scan_audio_and_merge_subtitles(audio_info, job, whisper_prompt=""):
    transcript = ""
    if audio_info:
        last_time = 0
        audio_file = audio_info["separate_wav_filepath"]
        segments_duration = audio_info["speech_duration"]
        try:
            print(f"正在提取音频：{audio_file}")
            result = query_gaia_whisper(audio_file, whisper_prompt)
            this_text = result["text"]
            print(f"{audio_file}识别结果：{this_text}")
            final_text_list = []
            paragraphs = this_text.split("\n")
            for i, paragraph in enumerate(paragraphs):
                pattern = r'\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s*(.*)'
                time_format = "%H:%M:%S.%f"
                match = re.match(pattern, paragraph)
                if match and match.group(3):
                    start_time = match.group(1)
                    end_time = match.group(2)
                    sentence = match.group(3).strip()
                    start_time = datetime.strptime(start_time, time_format)
                    end_time = datetime.strptime(end_time, time_format)
                    audio_duration_delta = timedelta(seconds=last_time)
                    start_time += audio_duration_delta
                    end_time += audio_duration_delta
                    start_time = start_time.strftime(time_format)[:-3]  # 去掉微秒部分后面的3位
                    end_time = end_time.strftime(time_format)[:-3]
                    final_text_list.append(f"[{start_time} --> {end_time}]  {sentence}")
            this_text = "\n".join(final_text_list)
            last_time += segments_duration
            if transcript:
                transcript += "\n"
            transcript += this_text
        except Exception as e:
            print(f"{audio_file} whisper报错 {e}")
            redis_client = get_redis_client()
            task_queue = Queue("video_tasks", connection=redis_client)
            job.retry(queue=task_queue, pipeline=None)
        print(f"音频已提取并保存")
        return transcript
    else:
        print("音频提取失败，已退出程序。")
        return