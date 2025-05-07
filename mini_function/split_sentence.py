from datetime import datetime, timedelta
from mini_function.query_function import gaia_gpt_chat
import re

time_format = "%H:%M:%S.%f"
s_pattern = r'\s{2,}'
pattern = r'[。？！\.?!]'


def split_sentence(sentence, start_time, end_time):
    this_list = []
    if len(sentence) > 140:
        check_split = "Please add commas and periods as needed to indicate sentence breaks. Return ONLY the modified text, with no explanations, comments, or statements about existing punctuation."
        final_sentence = gaia_gpt_chat(check_split, sentence)
        if re.search(pattern, final_sentence):
            start_timestamps = datetime.strptime(start_time, time_format)
            end_timestamps = datetime.strptime(end_time, time_format)
            time_difference = end_timestamps - start_timestamps
            # 计算语速
            total_text_length = len(final_sentence)
            split_text_list = re.split('。|？|！|\. |\."|\?|!', final_sentence.rstrip('。？！."?!'))
            for idx, item in enumerate(split_text_list):
                item = item.strip()
                this_text_length = len(item)
                this_start_timestamps = datetime.strptime(start_time, time_format)
                value_to_add = time_difference.total_seconds() * this_text_length / total_text_length
                new_timestamps = this_start_timestamps + timedelta(seconds=value_to_add)
                new_end_time = new_timestamps.strftime(time_format)[:-3]
                this_list.append(f"[{start_time} --> {new_end_time}]  {re.sub(s_pattern, ' ', item)}")
                start_time = new_end_time
        else:
            this_list.append(f"[{start_time} --> {end_time}]  {re.sub(s_pattern, ' ', final_sentence)}")
    else:
        this_list.append(f"[{start_time} --> {end_time}]  {re.sub(s_pattern, ' ', sentence)}")
    return this_list