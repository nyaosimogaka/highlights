import streamlit as st
import pandas as pd
import tempfile
import os
from moviepy import VideoFileClip
from summarizer import summarize_video
from datetime import datetime

st.set_page_config(page_title="Video Processing", layout="wide")
st.sidebar.title("🧰 Tools")
tool = st.sidebar.radio("Select a tool", ["🎬 Video Processing", "📊 Model Comparison"])

# Shared function: Extract frames
def extract_frames(video_path, frame_dir, fps=1):
    video = VideoFileClip(video_path)
    os.makedirs(frame_dir, exist_ok=True)
    for i, frame in enumerate(video.iter_frames(fps=fps)):
        frame_path = os.path.join(frame_dir, f"frame_{i:04d}.jpg")
        video.save_frame(frame_path, t=i)
    return frame_dir

# Shared function: Convert video format
def convert_video_format(video_path, output_format):
    output_path = os.path.splitext(video_path)[0] + f".{output_format}"
    clip = VideoFileClip(video_path)
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

def is_valid_time_format(t):
    try:
        datetime.strptime(t, "%H:%M:%S")
        return True
    except ValueError:
        return False

# ---------------- VIDEO PROCESSING ---------------- #
if tool == "🎬 Video Processing":
    st.title("🎬 Automated Video Processing")

    # -------- UPLOAD SECTION -------- #
    with st.container(border=True):
        st.header("📤 Upload Section")
        video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])

    # -------- OUTPUT SECTION -------- #
    if video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            tmp_video.write(video_file.read())
            tmp_video_path = tmp_video.name

        with st.container(border=True):
            st.header("📁 Output Section")

            tabs = st.tabs(["📸 Extract Frames", "🎞 Convert Video", "✂️ Summarize Video"])

            # ----- Tab: Extract Frames -----
            with tabs[0]:
                fps = st.slider("Select frame rate (FPS)", 1, 10, value=1)
                if st.button("Extract Frames"):
                    with st.spinner("Extracting frames..."):
                        frame_dir = extract_frames(tmp_video_path, "frames", fps=fps)
                        st.success("Frames extracted to 'frames/' folder.")
                        # Optional: Preview few extracted frames (every nth)
                        sample_frames = [os.path.join(frame_dir, f) for f in sorted(os.listdir(frame_dir))[:10]]
                        cols = st.columns(5)
                        for i, frame_path in enumerate(sample_frames):
                            with cols[i % 5]:
                                st.image(frame_path, caption=os.path.basename(frame_path), use_column_width=True)

            # ----- Tab: Convert Video -----
            with tabs[1]:
                output_format = st.selectbox("Select output format", ["avi", "mov", "mp4"])
                if st.button("Convert Video Format"):
                    with st.spinner("Converting video..."):
                        converted = convert_video_format(tmp_video_path, output_format)
                    with open(converted, "rb") as f:
                        st.download_button("📥 Download Converted Video", f, file_name=f"converted.{output_format}", mime="video/*")

            # ----- Tab: Summarize Video -----
            with tabs[2]:
                st.subheader("Timestamps Input")
                method = st.radio("Choose input method", ["Upload CSV", "Manual Input"])

                time_ranges = []
                if method == "Upload CSV":
                    csv_file = st.file_uploader("Upload CSV with 'Start' and 'Stop' columns", type=["csv"])
                else:
                    st.info("Enter up to 5 timestamp ranges in HH:MM:SS:SS format")
                    for i in range(5):
                        st.markdown(f"**Timestamp {i+1}**")
                        cols = st.columns(2)
                        with cols[0]:
                            start = st.text_input(f"Start {i+1}", value="00:00:00", key=f"start_{i}")
                        with cols[1]:
                            stop = st.text_input(f"Stop {i+1}", value="00:00:00", key=f"stop_{i}")

                        if is_valid_time_format(start) and is_valid_time_format(stop):
                            start_dt = datetime.strptime(start, "%H:%M:%S")
                            stop_dt = datetime.strptime(stop, "%H:%M:%S")
                            if stop_dt > start_dt:
                                time_ranges.append({"Start": start, "Stop": stop})
                            else:
                                st.error(f"Stop time must be greater than start time for Timestamp {i+1}")
                        else:
                            st.warning(f"Please enter valid HH:MM:SS values for Timestamp {i+1}")

                include_audio = st.checkbox("Include audio in summary", value=True)

                if st.button("Generate Summary Video"):
                    if method == "Upload CSV" and csv_file:
                        timestamps_df = pd.read_csv(csv_file)
                    else:
                        timestamps_df = pd.DataFrame(time_ranges)

                    if not {"Start", "Stop"}.issubset(timestamps_df.columns):
                        st.error("CSV must have 'Start' and 'Stop' columns.")
                    else:
                        output_path = "summary_output.mp4"
                        with st.spinner("Creating summary..."):
                            summarize_video(tmp_video_path, timestamps_df, output_path, audio=include_audio)
                        st.success("✅ Summary video ready!")
                        with open(output_path, "rb") as f:
                            st.download_button("📥 Download Summary", f, file_name="summary.mp4", mime="video/mp4")

# ---------------- MODEL COMPARISON ---------------- #
elif tool == "📊 Model Comparison":
    st.title("📊 Model Comparison - Soccer Player & Ball Detection/Tracking")
    st.info("This section will let users upload a video and compare performance of different player and ball detection/tracking models.")

    st.markdown("🚧 *Work in progress...*")
    st.markdown("- Model selection UI")
    st.markdown("- Video inference")
    st.markdown("- Side-by-side comparison")

    st.warning("Functionality coming soon!")
