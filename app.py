import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# কুকি ফাইলের নাম (নিশ্চিত করুন এই ফাইলটি আপনার মেইন ডিরেক্টরিতে আছে)
COOKIE_FILE = 'youtube_cookies.txt'

# Render-এ FFmpeg পাথ সেটআপ
FFMPEG_PATH = '/usr/bin/ffmpeg' if os.path.exists('/usr/bin/ffmpeg') else 'ffmpeg'

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                ydl_opts = {
                    'cookiefile': COOKIE_FILE,
                    'ffmpeg_location': FFMPEG_PATH,
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_info = {
                        'title': info.get('title'),
                        'thumbnail': info.get('thumbnail'),
                        'url': url
                    }
            except Exception as e:
                print(f"Extraction Error: {e}")
                
    return render_template('index.html', video_info=video_info)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    quality = request.form.get('quality', '720p')
    
    ydl_opts = {
        'cookiefile': COOKIE_FILE,
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestvideo[height<=720]+bestaudio/best' if quality == '720p' else 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # এক্সটেনশন চেক (MP4 নিশ্চিত করা)
            base_name = os.path.splitext(filename)[0]
            final_file = base_name + ".mp4"
            
            target_file = final_file if os.path.exists(final_file) else filename
            return send_file(target_file, as_attachment=True)
            
    except Exception as e:
        print(f"Download Error: {e}")
        return f"Download Error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

