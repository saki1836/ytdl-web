import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

# ডিরেক্টরি এবং ফাইলের পাথ সেটআপ
base_path = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(base_path, 'youtube_cookies.txt')
DOWNLOAD_FOLDER = os.path.join(base_path, 'downloads')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# রেন্ডার সার্ভারের জন্য FFmpeg পাথ
FFMPEG_PATH = os.environ.get('FFMPEG_BINARY', '/usr/bin/ffmpeg')

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                # আপনার দেওয়া ydl_opts কনফিগারেশন
                ydl_opts = {
                    'cookiefile': COOKIE_FILE,
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_info = {
                        'title': info.get('title'),
                        'thumbnail': info.get('thumbnail'),
                        'url': url
                    }
            except Exception as e:
                error = "YouTube is blocking the request. Please update your cookies."
                print(f"Extraction Error: {e}")
                
    return render_template('index.html', video_info=video_info, error=error)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    quality = request.form.get('quality', '720p')
    
    # ডাউনলোডের জন্য বিস্তারিত কনফিগারেশন
    ydl_opts = {
        'cookiefile': COOKIE_FILE,
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestvideo[height<=720]+bestaudio/best' if quality == '720p' else 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base_name = os.path.splitext(filename)[0]
            final_file = base_name + ".mp4"
            
            target = final_file if os.path.exists(final_file) else filename
            return send_file(target, as_attachment=True)
    except Exception as e:
        print(f"Download Error: {e}")
        return f"Download Failed: {str(e)}"

if __name__ == '__main__':
    # রেন্ডার পোর্টের জন্য কনফিগারেশন
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

