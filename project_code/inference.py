import traceback
import torch
import io
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
from transformers.pipelines.audio_utils import ffmpeg_read
from fastapi import Response


def model_fn():
    device = 0 if torch.cuda.is_available() else "cpu"
    # "bengaliAI/tugstugi_bengaliai-asr_whisper-medium" is the model.
    processor = AutoProcessor.from_pretrained("model")
    model = AutoModelForSpeechSeq2Seq.from_pretrained("model")
    pipe = pipeline(
        task="automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=30,
        device=device,
    )
    return pipe

def input_fn(request_body, request_content_type, sampling_rate):
    """Deserialize and prepare the input."""
    if request_content_type == 'audio/wav': # Or your audio content type
        audio_bytes = io.BytesIO(request_body)
        # Load the audio using librosa or another library.
        audio_data = ffmpeg_read(audio_bytes.getvalue(), sampling_rate=sampling_rate)
        return audio_data


def predict_fn(input_data, model_pipe):
    try:
        inputs_dict = {"raw": input_data, "sampling_rate": model_pipe.feature_extractor.sampling_rate}
        result = model_pipe(inputs_dict,
                      batch_size=8)
        return result["text"]
    except Exception as e:
        print(f"Error during prediction: {e}. Traceback: {traceback.format_exc()}")

def output_fn(transcript, accept='application/json'):
    """
    Format the prediction output as specified.
    """
    import json
    response = {'transcription': transcript}
    if accept == 'application/json':
        return Response(
            content=json.dumps(response),
            media_type=accept,
            status_code=200
        )
    else:
        raise ValueError(f"Unsupported accept type: {accept}")