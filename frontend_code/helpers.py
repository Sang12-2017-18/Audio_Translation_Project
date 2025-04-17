import base64

import librosa
import json
import requests
import soundfile as sf
import io
import math
import os
import yt_dlp
import boto3
from requests_toolbelt.multipart.encoder import MultipartEncoder
from botocore.config import Config

def post_request(endpoint: str, payload: dict):
    from frontend_code.constants import API_BASE
    try:
        response = requests.post(f"{API_BASE}{endpoint}", json=payload)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def extract_audio(youtube_url: str, start: int, end: int):
    return post_request("/download_youtube_video", {
        "youtube_url": youtube_url,
        "start_time": start,
        "end_time": end
    })

def invoke_chunk(chunk):
    from frontend_code.constants import SAGEMAKER_ENDPOINT
    aws_config = Config(
        read_timeout=120,
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )
    sagemaker_client = boto3.client('sagemaker-runtime', config=aws_config)

    # Create a multipart encoder for the chunk
    mp_encoder = MultipartEncoder(
        fields={
            "file": ("chunk.wav", chunk, "audio/wav")
        }
    )

    # Invoke the SageMaker endpoint
    response = sagemaker_client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType=mp_encoder.content_type,
        Body=mp_encoder.to_string()
    )

    result = response["Body"].read().decode("utf-8")
    result_json = json.loads(result)
    return result_json["transcription"]

def split_audio_into_chunks(file_bytes, chunk_duration_sec=20, target_rate=16000):
    # Load and resample the audio
    y, sr = librosa.load(io.BytesIO(file_bytes), sr=target_rate, mono=True)

    total_duration_sec = len(y) / sr
    total_chunks = math.ceil(total_duration_sec / chunk_duration_sec)
    samples_per_chunk = chunk_duration_sec * sr

    chunks = []
    for i in range(total_chunks):
        start_sample = int(i * samples_per_chunk)
        end_sample = int(min((i + 1) * samples_per_chunk, len(y)))
        chunk_data = y[start_sample:end_sample]

        # Save chunk to BytesIO
        buffer = io.BytesIO()
        sf.write(buffer, chunk_data, samplerate=target_rate, format="WAV")
        buffer.seek(0)
        chunks.append(buffer)

    return chunks


def transcribe_audio(audio_file_path: str = None, file_bytes: bytes = None):
    if audio_file_path:
        return post_request("/transcribe_audio", {"audio_url": audio_file_path})
    elif file_bytes:
        encoded_bytes = base64.b64encode(file_bytes).decode("utf-8")
        return post_request("/transcribe_audio", {"file_bytes": encoded_bytes})
    return None, "No valid input for transcription."


def translate_text(transcript: str):
    return post_request("/translate", {"transcript": transcript})

def download_youtube_audio(youtube_url: str, output_path: str = ".", start_time: int = None, end_time: int = None):
    """Downloads audio from a YouTube URL."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(id)s.%(ext)s',
            # "download_ranges": lambda _, i: [(start_time, end_time)] if i == 0 else [],
            'postprocessor_args': ['-ss', str(start_time - 2), '-to', str(end_time + 2)],  # for accurate trimming.
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'aac'}],
            "verbose": False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            final_filename = ydl.prepare_filename(info_dict, outtmpl=f'{output_path}/%(id)s.%(ext)s')
        final_filename = final_filename.rsplit(".", maxsplit=1)[0] + ".m4a"  # Change to m4a extension
        file_path = preprocess_audio(final_filename, target_sample_rate=16000)
        ## Upload to S3 in case of QA env
        return file_path, None
    except yt_dlp.DownloadError as e:
        print(f"Download error: {e}")
        return None, str(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, str(e)

def preprocess_audio(file_path: str,
                     target_sample_rate: int = 16000):
    """
    Preprocesses the video file for transcription.
    The final output file should be a mono-channel audio file, with WAV extension and a sample rate of 16kHz.
    :param file_path: The path of the audio file
    :param target_sample_rate: The target sample rate for the audio file.
    :return:
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None
    # Load the audio file
    filename_with_extension = os.path.basename(file_path)
    filename, file_ext = os.path.splitext(filename_with_extension)
    # change file extension to wav, which can easily be used by transcription model
    file_ext = ".wav"
    output_file = f"{filename}_processed{file_ext}"
    output_file_path = os.path.join(os.path.dirname(file_path), output_file)
    y, sr = librosa.load(file_path, sr=None, mono=False)  # Load as-is
    # Convert to mono (if not already mono)
    if len(y.shape) > 1:  # Check if audio is multichannel
        y = librosa.to_mono(y)
    # Resample to 16 kHz
    y_resampled = librosa.resample(y, orig_sr=sr, target_sr=target_sample_rate)
    # Save the processed audio
    sf.write(output_file_path, y_resampled, target_sample_rate, format="WAV")
    # Upload file to S3 in case of QA env
    print(f"Processed audio saved to {output_file}")
    return output_file_path