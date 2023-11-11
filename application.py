from flask import Flask, render_template, request, Response, send_file
import yt_dlp
import subprocess
import datetime  # For generating a timestamp
import uuid 
application = Flask(__name__)


def format_time(time_str):
    components = time_str.split(':')
    while len(components) < 3:
        components.insert(0, '0')
    formatted_time = [component.zfill(2) for component in components[:3]]
    return ':'.join(formatted_time)

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('video_url')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    if not video_url:
        return 'Video URL is required.'
    
    # Generate a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Generate a unique identifier
    unique_id = str(uuid.uuid4())

    # Construct a unique filename by combining the timestamp and unique identifier
    new_filename = f'new_file_{timestamp}_{unique_id}'

    ydl_opts = {
        'outtmpl': f'downloads/{new_filename}.mp4',
        'format': 'best',  # Choose the best available format
        'quiet': True,  # Suppress yt-dlp console output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)

        if 'entries' in info_dict:
            info_dict = info_dict['entries'][0]

        original_filename = f'downloads/{new_filename}.mp4'
        converted_filename = f'downloads/{new_filename}_converted.mp4'
        ydl.download([video_url])
        #renames original filename to santized filename to fit ffmpeg argument
    
       

    formatted_start_time = format_time(start_time)
    formatted_end_time = format_time(end_time)

    if formatted_start_time and formatted_end_time:
        # Convert the video with FFmpeg
        ffmpeg_command = [
            'ffmpeg',
            '-i', original_filename,
            '-ss', formatted_start_time,
            '-to', formatted_end_time,
            '-c:v', 'copy',
            '-c:a', 'copy',
            converted_filename
        ]

        try:
            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("FFmpeg command executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing FFmpeg command: {e}")
            print(f"FFmpeg output (stdout): {e.stdout}")
            print(f"FFmpeg error output (stderr): {e.stderr}")
        else:
            print(f'Converted filename: {converted_filename}')

        response = send_file(converted_filename, as_attachment=True)
        return response
    
    
    
    

if __name__ == '__main__':
    application.run(host='0.0.0.0', port= 8000 ,debug=True)
