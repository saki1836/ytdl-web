import os
from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

# ডাউলোড ফোল্ডার তৈরি
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# FFmpeg path setup for Render
FFMPEG_PATH = '/usr/bin/ffmpeg' if os.path.exists('/usr/bin/ffmpeg') else 'ffmpeg'

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                # Extraction options with User-Agent to avoid bot detection
                ydl_opts = {
                    'ffmpeg_location': FFMPEG_PATH,
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    # Video preview link check
                    video_url = next((f['url'] for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none'), None)
                    
                    video_info = {
                        'title': info.get('title'),
                        'thumbnail': info.get('thumbnail'),
                        'url': url,
                        'preview_url': video_url
                    }
            except Exception as e:
                print(f"Extraction Error: {e}")
                
    return render_template('index.html', video_info=video_info)

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    quality = request.form.get('quality')
    
    # Common options for all downloads
    ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'nocheckcertificate': True,
    }

    # Format selection logic
    if quality == "1080p":
        ydl_opts.update({'format': 'bestvideo[height<=1080]+bestaudio/best', 'merge_output_format': 'mp4'})
    elif quality == "720p":
        ydl_opts.update({'format': 'bestvideo[height<=720]+bestaudio/best', 'merge_output_format': 'mp4'})
    elif quality == "360p":
        ydl_opts.update({'format': 'best[height<=360]', 'merge_output_format': 'mp4'})
    elif quality == "mp3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Extension fix for MP3 or MP4
            if quality == "mp3":
                file_path = os.path.splitext(file_path)[0] + ".mp3"
            elif 'merge_output_format' in ydl_opts:
                file_path = os.path.splitext(file_path)[0] + ".mp4"

        return send_file(file_path, as_attachment=True)
        
    except Exception as error:
        print(f"Download Error: {error}")
        return f"Error: {error}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

