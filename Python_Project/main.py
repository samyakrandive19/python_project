import streamlit as st
import yt_dlp
import os
import imageio_ffmpeg

st.set_page_config(page_title="YouTube Downloader Pro", page_icon="🎬")

st.title("🎬 YouTube Downloader Pro")


if "stop" not in st.session_state:
    st.session_state.stop = False

url = st.text_input("🔗 Enter YouTube URL")
download_type = st.radio("Select Type", ["Video", "Audio (MP3)"])
quality = st.selectbox("Quality", ["1080p", "720p", "480p", "360p"])

col1, col2 = st.columns(2)

start = col1.button("🚀 Download")
stop_btn = col2.button("🛑 Stop")

st.caption("⚠️ Disclaimer: This can be only used for publicly available YouTube videos")



if stop_btn:
    st.session_state.stop = True
    st.warning("⛔ Stopping download...")


status = st.empty()


def progress_hook(d):
    if st.session_state.stop:
        raise Exception("Download stopped by user")

    if d['status'] == 'downloading':
        status.info(f"⬇ {d['_percent_str']} downloaded")
    elif d['status'] == 'finished':
        status.success("✅ Download finished, processing...")


if start:

    st.session_state.stop = False  

    if not url:
        st.warning("Enter URL first!")
        st.stop()

    try:
        status.info("🔍 Getting video info...")

        output_path = "downloads"
        os.makedirs(output_path, exist_ok=True)

        
        with yt_dlp.YoutubeDL({
            'quiet': True,
            'noplaylist': True
        }) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get("title", "video")
        thumbnail = info.get("thumbnail")

        if thumbnail:
            st.image(thumbnail)

        
        if download_type == "Video":
            format_code = f"best[height<={quality[:-1]}]"
        else:
            format_code = "bestaudio/best"

        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': format_code,
            'noplaylist': True,
            'progress_hooks': [progress_hook],  #  important
            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        }

        if download_type == "Audio (MP3)":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]

        status.info("⬇ Downloading...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not st.session_state.stop:
            status.success("✅ Download Complete!")

            
            files = os.listdir(output_path)
            latest_file = max(
                [os.path.join(output_path, f) for f in files],
                key=os.path.getctime
            )

            with open(latest_file, "rb") as f:
                st.download_button(
                    "⬇ Download File",
                    f,
                    file_name=os.path.basename(latest_file)
                )

    except Exception as e:
        if "stopped by user" in str(e):
            status.warning("⛔ Download stopped successfully!")
        else:
            import traceback
            st.error("❌ Error occurred")
            st.code(traceback.format_exc())