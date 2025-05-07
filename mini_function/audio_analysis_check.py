from pyAudioAnalysis import audioTrainTest as aT

def audio_analysis_check(wav_filepath):
    threshold = 0.4
    try:
        file_name = wav_filepath.split("/")[-1]
        check_type = aT.file_classification(wav_filepath, "dataknnSM", "knn")
        if check_type and check_type[0] != -1:
            result = {key: value for key, value in zip(check_type[2], check_type[1])}
            mix = result.get("mix", 0)
            music = result.get("music", 0)
            noise = result.get("noise", 0)
            voice = result.get("voice", 0)

            if music + noise == 1:
                threshold = 1
            elif voice == 1:
                threshold = 0
            elif voice + mix == 1 and voice > mix:
                threshold = 0.2
            else:
                threshold = max(0.2, round((1 - (voice + 0.5 * mix)) * 0.8, 1))
            print(f"音频: {file_name} 分析结果: {result}, 阈值: {threshold}")
    except Exception as e:
        print(f"音频分析失败：{e}")

    return threshold
