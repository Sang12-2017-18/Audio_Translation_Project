## This is the fastApi app.
import base64
import os.path
import json
from frontend_code.constants import GEMINI_API_KEY, PROMPT_TEMPLATE, GEMINI_MODEL
from frontend_code.helpers import split_audio_into_chunks, invoke_chunk

from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/download_youtube_video")
def download_video(
        youtube_url: str,
        start_time: int,
        end_time: int,
):
    output_path = "./audio_data_app"
    output_path = os.path.abspath(output_path)
    from frontend_code.helpers import download_youtube_audio
    final_filename, error_res = download_youtube_audio(youtube_url, output_path, start_time=start_time,
                                                       end_time=end_time)
    if error_res:
        return {
            "success": False,
            "audio_file": None,
            "error": error_res
        }
    return {
        "success": True,
        "audio_file": final_filename,
        "error": None
    }


@app.post("/transcribe_audio")
async def transcribe_audio(
        request: Request
):
    try:
        import json
        data = await request.json()
        audio_path = data.get("audio_path")
        file_bytes = data.get("file_bytes")
        if audio_path:
            audio_bytes = open(audio_path, 'rb').read()
        else:
            audio_bytes = file_bytes
            audio_bytes = base64.b64decode(audio_bytes)
        if not audio_bytes:
            raise ValueError("No audio data provided")
        # Split the audio into chunks
        chunks = split_audio_into_chunks(audio_bytes, chunk_duration_sec=20, target_rate=16000)
        # Initialize the results list
        results = []
        # Process each chunk
        for chunk in chunks:
            # Invoke the SageMaker endpoint for each chunk
            result_str = invoke_chunk(chunk)
            if not result_str:
                print("Empty response from the server")
            results.append(result_str)
        transcript = " ".join(results)
        print(f"{transcript[:100]}")
        return {
            "success": True,
            "transcript": transcript
        }
    except Exception as e:
        print(f"Exception: {e}")
        return {
            "success": False,
            "error": str(e),
            "transcript": None
        }


@app.post("/translate")
async def translate_text(
        request: Request
):
    # make request to translation service
    try:
        data = await request.json()
        transcript = data.get("transcript")
        if not transcript:
            raise ValueError("transcript is required")
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt_str = PROMPT_TEMPLATE.replace("{Bengali Text}", transcript)
        response = client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt_str,
        )
        response_text = response.text if response.text else ""
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "")
        # extract the first match
        # convert to json
        response_json = json.loads(response_text)
        translation = response_json.get("translation", "")
        if not translation:
            raise ValueError("Translation not found in response")
        return {
            "success": True,
            "translation": translation
        }
    except Exception as e:
        print(f"Translation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "translation": None
        }
