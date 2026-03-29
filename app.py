import os
from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

# ডাউলোড ফোল্ডার তৈরি
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Render-এর জন্য FFmpeg লোকেশন ডিটেক্ট করা
# যদি লিনাক্স সার্ভারে থাকে তবে /usr/bin/ffmpeg নিবে, নাহলে লোকাল 'ffmpeg' নিবে
FFMPEG_PATH = '/usr/bin/ffmpeg' if os.path.exists('/usr/bin/ffmpeg') else 'ffmpeg'

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            ydl_opts = {}
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
            print(f"Error: {e}")
            
    return render_template('index.html', video_info=video_info)

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    quality = request.form.get('quality')
    
    # কমন অপশন যা সব ফরম্যাটেই লাগবে
    base_opts = {
        'ffmpeg_location': FFMPEG_PATH,  # FFmpeg লোকেশন এখানে অ্যাড করা হয়েছে
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    }

    # ফরম্যাট সিলেকশন লজিক
    if quality == "1080p":
        ydl_opts = {**base_opts, 'format': 'bestvideo[height<=1080]+bestaudio/best', 'merge_output_format': 'mp4'}
    elif quality == "720p":
        ydl_opts = {**base_opts, 'format': 'bestvideo[height<=720]+bestaudio/best', 'merge_output_format': 'mp4'}
    elif quality == "360p":
        ydl_opts = {**base_opts, 'format': 'bestvideo[height<=360]+bestaudio/best', 'merge_output_format': 'mp4'}
    else: # MP3
        ydl_opts = {
            **base_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # এক্সটেনশন চেক (MP3 বা MP4 এর জন্য)
            if quality == "mp3":
                file_path = os.path.splitext(file_path)[0] + ".mp3"
            elif "merge_output_format" in ydl_opts:
                file_path = os.path.splitext(file_path)[0] + ".mp4"

        return send_file(file_path, as_attachment=True)
        
    except Exception as error:
        return f"Error downloading video: {error}"

if __name__ == '__main__':
    # Render-এর ডাইনামিক পোর্ট সাপোর্ট করার জন্য
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

