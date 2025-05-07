import librosa
import soundfile as sf
import subprocess
import noisereduce as nr


def separate_vocals(audio_path):
    audio, sr = librosa.load(audio_path)

    # 降噪处理
    reduced_noise = nr.reduce_noise(
        y=audio,
        sr=sr,
        stationary=True,
        prop_decrease=0.5
    )
    separate_output_path = audio_path.replace(".wav", "_separate.wav")
    # 保存结果
    sf.write(separate_output_path, reduced_noise, sr)
    # ffmpeg -i input.wav -filter:a "loudnorm=I=-20:TP=-2:LRA=11" output.wav
    big_output_path = audio_path.replace(".wav", "_separate_big.wav")
    output_path = big_output_path
    command = [
        'ffmpeg',
        '-i', separate_output_path,
        '-filter:a', 'loudnorm=I=-12:TP=-2:LRA=11', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
        big_output_path
    ]
    subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_path


if __name__ == "__main__":
    separate_vocals("example/mix_test.wav")
