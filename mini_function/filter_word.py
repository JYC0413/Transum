import re
import emoji
from mini_function.query_function import gaia_gpt_chat

time_format = "%H:%M:%S.%f"
s_pattern = r'\s{2,}|>>\s'
end_match_pattern = r'[.!?。！？]$|\."$|\。”$'
path_pattern = r'[。？！?!]|\."|\。”|\. '

all_query_text = ""
query_gemini_false = False


def find_repeated_match(paragraphs):
    match_counter = {}

    for i, paragraph in enumerate(paragraphs):
        try:
            pattern = r'\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s*(.*)'
            match = re.match(pattern, paragraph)
            if match and match.group(3):
                match_text = match.group(3)

                match_counter[match_text] = match_counter.get(match_text, 0) + 1
        except Exception as e:
            print(f"Error processing paragraph {i}: {e}")

    repeated_matches = [text for text, count in match_counter.items() if count >= 4]

    return repeated_matches


def time_to_seconds(time_str):
    hours, minutes, seconds, millisecond = map(int, re.findall(r'\d+', time_str))
    return hours * 3600 + minutes * 60 + seconds + millisecond / 1000


# 判断时间是否在区间内
def is_time_in_range(start_time_str, end_time_str, time_list):
    start_time_in_seconds = time_to_seconds(start_time_str)
    end_time_in_seconds = time_to_seconds(end_time_str)
    total_duration = end_time_in_seconds - start_time_in_seconds

    for start, end in time_list:
        if start <= start_time_in_seconds <= end or start_time_in_seconds == 0:
            if start <= end_time_in_seconds <= end and (
                    min(end, end_time_in_seconds) - max(start, start_time_in_seconds)) >= total_duration / 2:
                return True
    return False


def check_sentence(sentence, video_path):
    check_system_prompt = 'You are an expert linguist with knowledge of all world writing systems and languages. Analyze the following text and determine if it contains meaningful linguistic content in any human language, or if it appears to be random characters/gibberish.\n\nConsider these factors:\n1. Does this text use characters from a known writing system?\n2. Does it follow recognizable patterns of any human language?\n3. Does it contain identifiable words, morphemes, or common linguistic structures?\n4. Is the character distribution consistent with natural language statistics?\n\nAnswer with ONLY "YES" if it contains meaningful linguistic content in any language, or "NO" if it appears to be random characters or gibberish. No explanation needed.'
    check_sentence_status = gaia_gpt_chat(check_system_prompt, sentence)
    return "yes" in check_sentence_status.lower()


# def check_sentence(sentence, video_path):
#     try:
#         global all_query_text
#         global query_gemini_false
#         if all_query_text == "" and not query_gemini_false:
#             all_query_text = query_gemini_2_0_flash(video_path)
#         check_system_prompt = f"Check if the given text snippet is fully contained within this provided paragraph: '{all_query_text}'. Answer only 'yes' or 'no'."
#         check_sentence_status = gaia_gpt_chat(check_system_prompt, sentence, video_path, "")
#         return "yes" in check_sentence_status.lower()
#     except Exception as e:
#         print("检查句子失败:", e)
#         query_gemini_false = False
#         return True
#
#
# def query_gemini_2_0_flash(file):
#     my_file = client.files.upload(file=file)
#
#     response = client.models.generate_content(
#         model='gemini-2.0-flash',
#         contents=[
#             'Generate a transcript of the episode.',
#             my_file,
#         ]
#     )
#     return response.text

def have_emoji_match(sentence):
    try:
        sentence = sentence.encode().decode("utf-8-sig")
    except UnicodeDecodeError:
        pass  # 如果转换失败，则保持原文本
    for char in sentence:
        if emoji.is_emoji(char) or char in {"♪", "♫", "♬", "♩"}:
            print(f"检测到表情符号: {char}")
            return True
    return False


def contains_keywords(text, prompt=""):
    try:
        text = text.encode().decode("utf-8-sig")
    except UnicodeDecodeError:
        pass  # 如果转换失败，则保持原文本

    # 转换文本为小写，便于不区分大小写比较
    text_lower = text.lower()

    # 要检查的关键词列表
    keywords = [
        "www.",
        "amara.org",
        "明镜",
        "明鏡",
        "憂鬱",
        "subscribe",
        "suscríbete",
        "for watching",
        "作词",
        "作曲",
        "编曲",
        "录音",
        "混音",
        "母带",
        "订阅",
        "訂閱",
        ".com",
        "Thank you for",
        "https://",
    ]

    # 检查每个关键词是否在文本中
    for keyword in keywords:
        if keyword.lower() in text_lower or text_lower in prompt.lower():
            print(f"{text} 中检测到关键词: {keyword}")
            return True

    # 如果没有找到任何关键词，返回False
    return False


def filter_word(transcript, may_music, no_humans_list=[], whisper_prompt=""):
    global all_query_text
    all_query_text = ""
    paragraphs = transcript.split("\n")
    total_text = ""
    speech_duration = 0
    final_transcript = []
    have_repeated_match = find_repeated_match(paragraphs)
    for i, paragraph in enumerate(paragraphs):
        try:
            pattern = r'\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s*(.*)'
            match = re.match(pattern, paragraph)
            if match and match.group(3):
                start_time = match.group(1)
                end_time = match.group(2)
                sentence = match.group(3).strip()
                in_no_human_range_match = is_time_in_range(start_time, end_time, no_humans_list)
                have_emoji = have_emoji_match(sentence)
                have_warn_word = contains_keywords(sentence, whisper_prompt)
                # match_list = [sentence in have_repeated_match, in_no_human_range_match]
                if not sentence.startswith(("[", "{", "(", "*",
                                            "〈")) and not have_emoji and not have_warn_word and not in_no_human_range_match and (not may_music or sentence not in have_repeated_match):
                    final_sentence = re.sub(s_pattern, ' ', sentence)
                    final_text = f"[{start_time} --> {end_time}]  {final_sentence}"
                    final_transcript.append(final_text)
                    speech_duration += time_to_seconds(end_time) - time_to_seconds(start_time)
                    total_text += final_sentence + " "
        except Exception as e:
            print("合并timestamps失败:", e)
            return
    transcript = "\n".join(final_transcript)
    return {"transcript": transcript, "total_text": total_text, "speech_duration": speech_duration}


if __name__ == "main":
    filter_word("test/a.txt", "")
    print("Conversion complete")
