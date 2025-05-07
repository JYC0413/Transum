import math
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps


def get_silent_periods(audio_file_path, audio_duration, threshold=0.2):
    model = load_silero_vad()
    wav = read_audio(audio_file_path)
    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        threshold=threshold,  # Probability threshold for speech detection
        return_seconds=True,  # Return speech timestamps in seconds (default is samples)
    )
    no_humans_list = []
    if len(speech_timestamps) == 0:
        no_humans_list = [[0, math.ceil(audio_duration)]]
    else:
        for i in range(len(speech_timestamps)):
            if i == 0 and speech_timestamps[i]["start"] > 10:
                no_humans_list.append([0, math.floor(speech_timestamps[i]["start"])])
            if i > 0 and speech_timestamps[i]["start"] - speech_timestamps[i - 1]["end"] > 10:
                no_humans_list.append([math.ceil(speech_timestamps[i - 1]["end"]), math.floor(speech_timestamps[i]["start"])])

        # Add the last segment from the end of the last speech to the end of the audio
        if speech_timestamps[-1]["end"] < audio_duration:
            no_humans_list.append([math.ceil(speech_timestamps[-1]["end"]), math.ceil(audio_duration)])

    return no_humans_list
