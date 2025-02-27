import yt_dlp
import threading
import re
import os
import sys
import shutil

Name = ["YTDLP"]
Desc = ["Download videos with YTDLP"]
Webs = ["ytdlp.org"]
Real = ["1.2"]
Devs = ["Devid"]

if __name__ == "__main__":
    print(f"Please run this as Downloady -e {os.path.abspath(__file__)}")
    sys.exit(1)

def process_download(url, save_path, progress_callback=None):
    """Start the download process using yt-dlp and update the GUI progress bar."""
    thread = threading.Thread(target=download_with_yt_dlp, args=(url, save_path, progress_callback), daemon=True)
    thread.start()

def download_with_yt_dlp(url, output_folder, progress_callback=None):
    """Download the video using yt-dlp at the highest quality available and update progress."""
    ydl_opts = {
        'format': 'bv+ba/best',  # Ensure both best video and best audio are downloaded and merged
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'  # Ensure output is in MP4 format with both video and audio
        }],
        'noplaylist': True,
        'progress_hooks': [lambda d: progress_hook(d, progress_callback)],
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', 'unknown_title').replace("/", "_").replace("\\", "_")
        output_path = os.path.join(output_folder, f"{video_title}.mp4")
        
        ydl_opts['outtmpl'] = output_path
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    print(f"File saved as: {output_path}")
    move_out_of_watch_folder(output_path)

def move_out_of_watch_folder(file_path):
    """Move file out of 'watch' folder if it's inside one and delete the empty folder."""
    file_dir, file_name = os.path.split(file_path)
    parent_dir = os.path.dirname(file_dir)
    
    if os.path.basename(file_dir).lower() == "watch":
        new_path = os.path.join(parent_dir, file_name)
        shutil.move(file_path, new_path)
        os.rmdir(file_dir)  # Remove the empty 'watch' folder
        print(f"Moved {file_name} out of 'watch' folder to {new_path}")

def progress_hook(d, progress_callback):
    """Hook to display download progress and update GUI progress bar."""
    if d['status'] == 'downloading':
        percent_match = re.search(r"(\d+\.\d+)%", d['_percent_str'])
        percent = float(percent_match.group(1)) / 100 if percent_match else 0
        speed = d.get('_speed_str', 'Unknown')
        eta = d.get('_eta_str', 'Unknown')
        
        print(f"Downloading: {d['_percent_str']} | Speed: {speed} | ETA: {eta}")
        
        if progress_callback:
            progress_callback(percent)
    elif d['status'] == 'finished':
        print("Download complete!")
        if progress_callback:
            progress_callback(1.0)
