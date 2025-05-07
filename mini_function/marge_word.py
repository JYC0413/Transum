import re
from mini_function.query_function import gaia_gpt_chat
from datetime import datetime, timedelta
from mini_function.split_sentence import split_sentence

time_format = "%H:%M:%S.%f"
end_match_pattern = r'[.!?。！？]$|\."$|\。”$'
path_pattern = r'[。？！?!]|\."|\。”|\. '


def time_to_seconds(time_str):
    hours, minutes, seconds, millisecond = map(int, re.findall(r'\d+', time_str))
    return hours * 3600 + minutes * 60 + seconds + millisecond / 1000


# 判断时间是否在区间内
def is_time_in_range(start_time_str, end_time_str, time_list):
    start_time_in_seconds = time_to_seconds(start_time_str)
    end_time_in_seconds = time_to_seconds(end_time_str)
    for start, end in time_list:
        if start <= start_time_in_seconds <= end or start_time_in_seconds == 0:
            if start <= end_time_in_seconds <= end:
                return True
            else:
                return False
    return False


def marge_word(transcript, no_humans_list=[], youtube_link="", email_link=""):
    paragraphs = transcript.split("\n")
    final_transcript = []
    last_end = ""
    temp_sentence = ""
    for i, paragraph in enumerate(paragraphs):
        try:
            pattern = r'\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s*(.*)'
            match = re.match(pattern, paragraph)
            if match and match.group(3):
                start_time = match.group(1)
                end_time = match.group(2)
                sentence = match.group(3).strip()
                if not sentence.startswith(("[", "{", "(", "*", "〈")) and not is_time_in_range(start_time, end_time, no_humans_list):
                    if temp_sentence:
                        if sentence and ((sentence[0].isupper() and not (temp_sentence.endswith(',') or temp_sentence.endswith('，'))) or (last_end and time_to_seconds(start_time) - time_to_seconds(last_end) > 2000)):
                            check_prompt = 'You will receive an sentence or phrase. Your task is to determine whether the sentence is complete (i.e., expresses a full thought and could naturally be spoken or written as a standalone sentence, even if informal or without perfect punctuation). For example, if I say "So let is check this one out" you respond with "yes", if  I say "I rediscovered it and" you respond with "no"'
                            check_sentence = gaia_gpt_chat(check_prompt, temp_sentence)
                            print("check_sentence", check_sentence)
                            if "yes" in check_sentence.lower():
                                final_list = split_sentence(temp_sentence, last_end, start_time)
                                final_transcript.extend(final_list)
                            else:
                                if last_end:
                                    start_time = last_end
                                # 和旧数据拼起来
                                sentence = temp_sentence + " " + sentence
                                sentence = sentence.strip()
                        else:
                            if last_end:
                                start_time = last_end
                            # 和旧数据拼起来
                            sentence = temp_sentence + " " + sentence
                            sentence = sentence.strip()
                        temp_sentence = ""
                        last_end = ""
                    # 如果以标准的.!?结尾，这句话一定结束了
                    if re.search(end_match_pattern, sentence):
                        last_end = end_time
                        final_list = split_sentence(sentence, start_time, end_time)
                        final_transcript.extend(final_list)
                    # 否则如果里面有句号，那这一句话肯定也结束了，把内容分开
                    elif re.search(path_pattern, sentence):
                        # 计算时间差
                        start_timestamps = datetime.strptime(start_time, time_format)
                        end_timestamps = datetime.strptime(end_time, time_format)
                        time_difference = end_timestamps - start_timestamps
                        # 计算语速
                        total_text_length = len(sentence)
                        split_text_list = re.split('。|？|！|\. |\."|\?|!', sentence.rstrip('。？！."?!'))
                        for idx, item in enumerate(split_text_list):
                            item = item.strip()
                            if idx + 1 != len(split_text_list):
                                this_text_length = len(item)
                                this_start_timestamps = datetime.strptime(start_time, time_format)
                                value_to_add = time_difference.total_seconds() * this_text_length / total_text_length
                                new_timestamps = this_start_timestamps + timedelta(seconds=value_to_add)
                                new_end_time = new_timestamps.strftime(time_format)[:-3]
                                final_list = split_sentence(item, start_time, new_end_time)
                                final_transcript.extend(final_list)
                                start_time = new_end_time
                                last_end = new_end_time
                            elif i + 1 == len(paragraphs):
                                final_list = split_sentence(item, start_time, end_time)
                                final_transcript.extend(final_list)
                            else:
                                temp_sentence = item
                    elif i + 1 == len(paragraphs):
                        final_list = split_sentence(sentence, start_time, end_time)
                        final_transcript.extend(final_list)
                    else:
                        temp_sentence = sentence
                        last_end = start_time
                elif temp_sentence:
                    if last_end:
                        start_time = last_end
                    final_list = split_sentence(temp_sentence, start_time, end_time)
                    final_transcript.extend(final_list)
                    last_end = end_time
                    temp_sentence = ""
                if i + 1 == len(paragraphs) and temp_sentence:
                    final_list = split_sentence(temp_sentence, last_end, end_time)
                    final_transcript.extend(final_list)
        except Exception as e:
            print("合并timestamps失败:", e)
            return
    transcript = "\n".join(final_transcript)
    return transcript


if __name__ == "main":
    marge_word("test/a.txt", "")
    print("Conversion complete")