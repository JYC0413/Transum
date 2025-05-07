import json
import os
import requests
import shutil
import string
import random
import time
from datetime import datetime
from langdetect import detect
from rq import get_current_job

from mini_function.convert_to_srt import convert_to_srt
from mini_function.filter_word import filter_word
from mini_function.query_function import gaia_gpt_chat
from mini_function.save_file import save_file
from mini_function.scan_audio_and_merge_subtitles import scan_audio_and_merge_subtitles
from mini_function.split_audio_from_mp4 import split_audio_from_mp4
from mini_function.video_trans_to_mp4 import video_trans_to_mp4

whisper_prompt = ""
check_prompt = "Analyze the following text and determine if it is likely to be song lyrics. You don't need to know every song or lyric—just assess whether the text resembles song lyrics based on its structure, rhythm, rhyme patterns, and overall lyrical style rather than regular speech or prose. If the text is likely to be song lyrics, respond with \"yes.\" If not, respond with \"no.\" Only provide \"yes\" or \"no\" as the answer."


def process_video(video_file_url, callback_url, biz_id, result_type):
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y%m%d%H%M%S")
    letters = string.ascii_letters + string.digits
    save_folder = ''.join(random.choice(letters) for _ in range(6)) + timestamp
    os.makedirs(save_folder, exist_ok=True)
    job = get_current_job()
    start_time = datetime.now()
    video_file_name = save_file(video_file_url, save_folder)
    mp4_name = video_trans_to_mp4(video_file_name, save_folder)
    split_data = split_audio_from_mp4(mp4_name, save_folder)
    if split_data and split_data["separate_wav_filepath"] and split_data["threshold"] != 1:
        transcript_text = scan_audio_and_merge_subtitles(split_data, job, whisper_prompt)
        marge_transcript_data = filter_word(transcript_text, split_data["threshold"] >= 0.5, split_data["no_humans_list"], whisper_prompt)
        check_music_status = ""
        if marge_transcript_data["total_text"] == "":
            language = ""
        else:
            # if split_data["threshold"] >= 0.5:
            #     check_music_status = gaia_gpt_chat(check_prompt, marge_transcript_data["total_text"], video_file_url, save_folder)
            #     print(f"检测歌词: {check_music_status}")
            try:
                language = detect(marge_transcript_data["total_text"])
            except Exception as e:
                language = ""
                print(f"检测语言失败: {marge_transcript_data['total_text']}, {e}")
        result_data = {"biz_id": biz_id, "job_id": job.id, "speech_duration": marge_transcript_data["speech_duration"],
                       "language_code": language, "is_music": False}
        if 'yes' in check_music_status.lower():
            if "1" in result_type:
                result_data["srt"] = ""
            if "2" in result_type:
                result_data["total"] = ""
            if "3" in result_type:
                result_data["summarize"] = ""
        else:
            if "1" in result_type:
                srt_file_data = convert_to_srt(marge_transcript_data["transcript"], mp4_name)
                result_data["srt"] = srt_file_data
            if "2" in result_type:
                result_data["total"] = marge_transcript_data["total_text"]
            if "3" in result_type:
                summarize = ""
                if marge_transcript_data["total_text"] == "":
                    result_data["summarize"] = summarize
                else:
                    summarize_prompt = 'Please read the following video subtitles and summarize the main content of the video based on the subtitles. \nIf the subtitles contain meaningful information, provide a concise summary in English, regardless of the original language of the subtitles. \nIf the subtitles are too fragmented, incoherent, or contain only noise, chants, or unstructured words without a clear meaning, return an empty summary. \nDo not skip summarization if a meaningful interpretation can be made. Always attempt to summarize whenever possible. \nRespond strictly in the following JSON format without any extra text: \n{"status": "true", "summarize": "your_summary_here"} \nIf no meaningful summary can be generated, return: \n{"status": "false", "summarize": ""}'
                    try:
                        summarize_json = gaia_gpt_chat(summarize_prompt, marge_transcript_data["total_text"])
                        print(f"生成摘要: {summarize_json}")
                        status = json.loads(summarize_json)["status"]
                        summarize = json.loads(summarize_json)["summarize"]
                        if status == "true" and summarize:
                            result_data["summarize"] = summarize
                        else:
                            if language == "":
                                if "1" in result_type:
                                    result_data["srt"] = ""
                                if "2" in result_type:
                                    result_data["total"] = ""
                                result_data["speech_duration"] = 0
                            result_data["summarize"] = ""
                    except Exception as e:
                        print(f"生成摘要失败: {e}")
                        if language == "":
                            if "1" in result_type:
                                result_data["srt"] = ""
                            if "2" in result_type:
                                result_data["total"] = ""
                            result_data["speech_duration"] = 0
                        result_data["summarize"] = ""
    else:
        result_data = {"biz_id": biz_id, "job_id": job.id, "speech_duration": 0, "language_code": "", "is_music": True}
        if "1" in result_type:
            result_data["srt"] = ""
        if "2" in result_type:
            result_data["total"] = ""
        if "3" in result_type:
            result_data["summarize"] = ""
    json_result_data = json.dumps(result_data)
    print(json_result_data)
    num = 0
    while num < 5:
        try:
            response = requests.request("POST", callback_url, data=json_result_data)
            if response.status_code == 200:
                print("回调成功")
                end_time = datetime.now()
                elapsed_time = end_time - start_time
                elapsed_seconds = elapsed_time.total_seconds()
                print(f"程序总运行时长: {elapsed_seconds:.2f} 秒")
                shutil.rmtree(save_folder)
                break
            else:
                num += 1
                time.sleep(2)
                print(f"回调失败: {response.status_code}")
        except Exception as e:
            time.sleep(2)
            num += 1
            print(f"回调失败: {e}")


if __name__ == "__main__":
    process_video("https://d-2.myclapper.com/video/GoBpwrQVPl/f8daab406c62469085fbfb6f1869fd66.mp4", "https://api.videolangua.com/callback", "123", "1, 2, 3")
