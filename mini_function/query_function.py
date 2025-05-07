import os
import re
import time
import json
import requests
from dotenv import load_dotenv
from redis_conn import redis_conn

load_dotenv()

retry_time = 3

whisper_request_limit = os.getenv("WHISPER_REQUEST_LIMIT", 6)
api_request_limit = os.getenv("API_REQUEST_LIMIT", 3)
gaia_whisper_api_url = os.getenv("GAIA_WHISPER_API_URL")
gaia_chat_api_url = os.getenv("GAIA_CHAT_API_URL")
gaia_api_key = os.getenv("GAIA_API_KEY")


def query_gaia_whisper(audio_file_path, whisper_prompt="", language='auto'):
    headers = {
        # 'Authorization': 'Bearer ' + gaia_api_key
    }

    # 打开文件并准备发送请求
    files = {"file": open(audio_file_path, "rb")}
    data = {
        'language': language,
        'prompt': whisper_prompt
    }

    max_retries = retry_time
    attempt = 0
    while attempt < max_retries:
        while True:
            current_request_count = redis_conn.incr("whisper_request_count")
            if current_request_count > whisper_request_limit:
                redis_conn.decr("whisper_request_count")
                time.sleep(0.1)
            else:
                print(f"whisper count: {current_request_count}")
                break
        path = attempt % retry_time
        attempt += 1
        try:
            url = gaia_whisper_api_url
            response = requests.post(url, files=files, headers=headers, data=data)
            response.raise_for_status()  # 检查 HTTP 状态码，非 2xx 会抛出异常
            response_data = response.json()  # 解析 JSON 数据
            return response_data
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP 错误: {http_err}")
        except requests.exceptions.JSONDecodeError as json_err:
            print(f"JSON 解析失败: {json_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"请求失败: {req_err}")
        finally:
            redis_conn.decr("whisper_request_count")
        if path < retry_time - 1 and attempt < max_retries:
            retry_delay = 0.5
        else:
            retry_delay = 0
        print("whisper retry delay: ", retry_delay)
        time.sleep(retry_delay)  # 等待一段时间后重试


def gaia_gpt_chat(system_prompt, prompt, pass_num=0, end_num=0):
    payload = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + gaia_api_key
    }

    max_retries = retry_time
    attempt = 0

    while attempt < max_retries:
        while True:
            current_request_count = redis_conn.incr("llm_request_count")
            if current_request_count > api_request_limit:
                redis_conn.decr("llm_request_count")
                time.sleep(0.1)
            else:
                print(f"llm_count: {current_request_count}")
                break
        path = attempt % retry_time
        attempt += 1
        try:
            url = gaia_chat_api_url
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()  # 检查HTTP错误
            response_data = response.json()
            translation_data = response_data['choices'][0]['message']['content']
            return re.sub(r'^\.[a-zA-Z]+', '', translation_data).removeprefix("__':").strip()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed for {gaia_chat_api_url}. Error: {e}")
            if path < retry_time - 1 and attempt < max_retries:
                retry_delay = 0.5
            else:
                retry_delay = 0
            print("gaia node retry delay: ", retry_delay)
            time.sleep(retry_delay)  # 等待一段时间后重试
        finally:
            redis_conn.decr("llm_request_count")
