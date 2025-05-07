import os
import subprocess
from mini_function.separate_vocals import separate_vocals
from mini_function.get_silent_periods import get_silent_periods
from mini_function.audio_analysis_check import audio_analysis_check
from moviepy import AudioFileClip


def split_audio_from_mp4(mp4_filename, save_folder):
    try:
        # Extract audio from MP4 file and save as WAV
        wav_name = os.path.splitext(mp4_filename)[0]
        wav_filename = wav_name + '.wav'
        wav_filepath = os.path.join(save_folder, wav_filename)
        ffmpeg_command = [
            'ffmpeg',
            '-y',
            "-nostdin",
            '-i', os.path.join(save_folder, mp4_filename),
            '-q:a', '2',
            '-acodec', 'pcm_s16le',
            '-map', 'a',
            '-ar', '16000',
            '-af', 'aresample=16000',
            '-ac', '1',
            wav_filepath
        ]
        # Run the ffmpeg command
        # ffmpeg -y -i input.mp4 -q:a 2 -acodec pcm_s16le -map a -ar 16000 -af aresample=16000 -ac 1 output.wav
        print("🔊 Extracting audio from MP4 file...")
        subprocess.run(ffmpeg_command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        separate_wav_filepath = separate_vocals(wav_filepath)
        threshold = audio_analysis_check(wav_filepath)
        with AudioFileClip(separate_wav_filepath) as audio:
            duration = round(audio.duration, 2)
        print(f"总时长: {duration}")
        no_humans_list = get_silent_periods(separate_wav_filepath, duration, threshold)
        print("no_humans_list:", no_humans_list)
        return {"no_humans_list": no_humans_list, "separate_wav_filepath": separate_wav_filepath, "speech_duration": duration, "threshold": threshold}
    except Exception as e:
        print(f"从 {mp4_filename} 提取音频时出错：{e}")
        return None


if __name__ == "__main__":
    # Example usage
    split_audio_from_mp4("example/example_en_video.mp4", "")
    print("Audio extraction and splitting complete")
