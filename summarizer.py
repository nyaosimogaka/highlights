from moviepy import VideoFileClip, concatenate_videoclips
import pandas as pd
import datetime


def time_to_seconds(time_str):
    """Converts 'HH:MM:SS' or 'MM:SS' to seconds (float)."""
    try:
        t = datetime.datetime.strptime(time_str.strip(), "%H:%M:%S")
    except ValueError:
        t = datetime.datetime.strptime(time_str.strip(), "%M:%S")
    return t.hour * 3600 + t.minute * 60 + t.second


def summarize_video(video_path, timestamps_df, output_path="output.mp4", audio=True):
    try:
        video = VideoFileClip(video_path)
        print(f"Loaded video type: {type(video)}")

        subclips = []

        for index, row in timestamps_df.iterrows():
            start = time_to_seconds(str(row["Start"]))
            end = time_to_seconds(str(row["Stop"]))

            print(f"Adding subclip from {start} to {end}")
            subclip = video.subclipped(start, end)
            subclips.append(subclip)

        final_clip = concatenate_videoclips(subclips)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", audio=audio)
        return output_path
    except Exception as e:
        print(f"Error during video summarization: {e}")
        raise

