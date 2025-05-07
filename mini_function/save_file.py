import os
import re
import time
import requests
from urllib.parse import urlparse


def save_file(url, save_folder):
    num = 0
    filename = os.path.basename(urlparse(url).path)
    filename = re.sub(r'[\?].*$', '', filename)
    filepath = os.path.join(save_folder, filename)

# 如果请求成功，保存文件
    while num < 3:
        try:
            response = requests.get(url, allow_redirects=True)
            if response.status_code == 200:
                try:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    return filename
                except Exception as e:
                    print(f"❌ 无法保存文件：{url}, {e}")
        except Exception as e:
            print(f"❌ 发送请求失败：{url}, {e}")

        num += 1
        time.sleep(2)
        print(f"❌ 无法下载文件：{url}")



