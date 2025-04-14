from fastapi import FastAPI, UploadFile, File
from project_code.inference import input_fn, model_fn, predict_fn, output_fn
app = FastAPI()

# Load model and processor once when the container starts

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/invocations")
async def transcribe(file: UploadFile = File(...)):
    file_bytes = await file.read()
    audio_bytes = input_fn(file_bytes, file.content_type, 16000)
    model_pipe = model_fn()
    transcription = predict_fn(audio_bytes, model_pipe)
    return output_fn(transcription)
