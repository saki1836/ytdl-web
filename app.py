import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

# ডাউলোড ফোল্ডার তৈরি
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# কুকি ফাইলের সঠিক পাথ (ডিরেক্টরি সহ)
base_path = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(base_path, 'youtube_cookies.txt')

# FFmpeg পাথ সেটআপ (রেন্ডার এনভায়রনমেন্ট অনুযায়ী)
FFMPEG_PATH = os.environ.get('FFMPEG_BINARY', '/usr/bin/ffmpeg')

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
                    # বট ডিটেকশন এড়াতে অতিরিক্ত হেডার
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
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
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        # কুয়ালিটি সিলেকশন
        'format': 'bestvideo[height<=720]+bestaudio/best' if quality == '720p' else 'best',
        'merge_output_format': 'mp4',
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # ফাইল এক্সটেনশন ঠিক করা
            base_name = os.path.splitext(filename)[0]
            final_file = base_name + ".mp4"
            
            if os.path.exists(final_file):
                return send_file(final_file, as_attachment=True)
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        print(f"Download Error: {e}")
        return f"Error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

