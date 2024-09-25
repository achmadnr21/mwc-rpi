# in this file, we define the Stream procedure to perform the streaming process
import numpy as np
import cv2
from picamera2 import Picamera2
from datetime import datetime
import time
import subprocess
import os

TIMER = time.time()
def write_image(frame=None):
    global TIMER  # Menggunakan variabel global TIMER
    current_time = time.time()  # Mendapatkan waktu saat ini

    if current_time - TIMER >= 30:
        ds_dir = os.path.expanduser('~/dataset')
        print(f'saving : {ds_dir}')
        if not os.path.exists(ds_dir):
            os.makedirs(ds_dir)

        # Mendapatkan timestamp
        timestamp = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

        # Membuat nama file
        file_name = f'image_{timestamp}.jpg'

        # Menyimpan gambar ke direktori
        cv2.imwrite(f'{ds_dir}/{file_name}', frame)

        # Memperbarui TIMER setelah menyimpan gambar
        TIMER = current_time
# get faces
detector = cv2.CascadeClassifier('/home/markaswalet/markaswalet-stream/haarcascadeku/haarcascade_frontalface_default.xml')
def get_faces(image = None):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray)
    return faces
# Stream procedure

IMSIZE = (640, 480)
FPS = 15  # Adjust to your desired frame rate

# Initialize the PiCamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": IMSIZE}))


def stream_process(stream_ip = '103.193.179.252' ,stream_key='mwcdef'):
    # stream_key = 'mwcxx'
    # add         '-loglevel', 'error', to shut up the log

    # Old Preset
    # command = [
    #     'ffmpeg',
    #     '-loglevel', 'error',
    #     '-y',  # overwrite output files
    #     '-f', 'rawvideo',
    #     '-pix_fmt', 'rgb24',  # Changed to rgb24 to match XRGB8888 format
    #     '-s', f'{IMSIZE[0]}x{IMSIZE[1]}',  # size of the input video
    #     '-r', str(FPS),  # frames per second
    #     '-i', '-',  # input comes from a pipe
    #     '-c:v', 'libx264',  # video codec
    #     '-crf', '21',
    #     '-preset', 'veryfast',
    #     '-b:v', '750k',  # Adjust bitrate as needed for better quality
    #     '-maxrate', '750k',
    #     '-bufsize', '1500k',
    #     '-ac', '2',
    #     '-c:a', 'aac',  # Codec audio
    #     '-b:a', '128k',  # Bitrate audio
    #     '-f', 'flv',  # format for RTMP
    #     f'rtmp://{stream_ip}:1935/markaswalet-live/{stream_key}'  # RTMP server URL
    # ]


    # New preset
    command = [
        'ffmpeg',
        '-loglevel', 'error',
        '-y',  # overwrite output files
        '-f', 'rawvideo',
        '-pix_fmt', 'rgb24',  # Changed to rgb24 to match XRGB8888 format
        '-s', f'{IMSIZE[0]}x{IMSIZE[1]}',  # size of the input video
        '-r', str(FPS),  # frames per second
        '-i', '-',  # input comes from a pipe

        # Add dummy audio
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', # dummy audio input

        # Video settings
        '-c:v', 'libx264',  # video codec
        '-preset', 'ultrafast',
        '-b:v', '750k',  # Adjust bitrate as needed for better quality
        '-maxrate', '750k',
        '-bufsize', '1500k',
        '-pix_fmt', 'yuv420p', #standard pixel format for compatibility
        '-profile:v', 'baseline', #Baseline for better compatibility with mobile devices

        # Audio Setting
        
        '-c:a', 'aac',  # Codec audio
        '-b:a', '128k',  # Bitrate audio
        '-ac', '2',
        '-f', 'flv',  # format for RTMP
        f'rtmp://{stream_ip}:1935/markaswalet-live/{stream_key}'  # RTMP server URL
    ]

    # Start the camera
    print('\033c')
    print(f'====================== START STREAM  =============================')
    print(f'Start Streaming with stream id = {stream_key}')
    print(f'rtmp://{stream_ip}:1935/markaswalet-live/{stream_key}')
    print(f'====================== START CAMERA  =============================')
    picam2.start()
    print(f'====================== START SENDING =============================')
    # Start ffmpeg subprocess
    ffmpeg = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        while True:
            # Capture video frame
            frame = picam2.capture_array()
            if frame is None:
                break

            # frame_bgr = frame[:, :, 0:3]  # Extract RGB channels from XRGB8888

            # Convert from numpy array to OpenCV image format
            frame_bgr = np.asarray(frame[:, :, 0:3], dtype=np.uint8)
            frame_bgr = cv2.flip(frame_bgr, -1)
            write_image(frame_bgr)
            faces = get_faces(frame_bgr)
            # Get the current time
            current_time = datetime.now().strftime("%H:%M:%S")
            # Write it
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            
            for (x,y,w,h) in faces:
                cv2.rectangle(frame_rgb, (x,y), (x+w, y+h), (255,0,0),2) # red

            cv2.putText(frame_rgb, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA) # red
            try:
                ffmpeg.stdin.write(frame_rgb.tobytes())
            except Exception as e:
                print(f"Error writing to ffmpeg stdin: {e}")
                break


    except KeyboardInterrupt:
        print("Streaming stopped by user")

    finally:
        # Clean up
        print(f'====================== STREAM ERROR        =============================')
        ffmpeg.stdin.close()
        ffmpeg.wait()
        picam2.stop()
    print(f'====================== RE-STARTING PROCESS =============================\n\n\n')
    time.sleep(5)
