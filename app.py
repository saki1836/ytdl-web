import os
from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

# Download folder toiri kora
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            ydl_opts = {}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # Video preview link check (direct mp4 link thakle play hobe)
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
    
    # Format selection logic
    if quality == "1080p":
        ydl_opts = {'format': 'bestvideo[height<=1080]+bestaudio/best', 'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s', 'merge_output_format': 'mp4'}
    elif quality == "720p":
        ydl_opts = {'format': 'bestvideo[height<=720]+bestaudio/best', 'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s', 'merge_output_format': 'mp4'}
    elif quality == "360p":
        ydl_opts = {'format': 'best[height<=360]', 'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s'}
    else: # MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        # MP3 hole extension change hote pare tai safe check
        if quality == "mp3":
            file_path = os.path.splitext(file_path)[0] + ".mp3"

    @after_this_request
    def remove_file(response):
        try:
            # Download hoye gele file delete kore dibe server clean rakhte
            # os.remove(file_path) 
            pass
        except Exception as error:
            print(f"Error removing file: {error}")
        return response

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

