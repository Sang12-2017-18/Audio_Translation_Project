import json
from fastapi import FastAPI, UploadFile, File, Response
from project_code.inference import input_fn, model_fn, predict_fn, output_fn
app = FastAPI()

# Load model and processor once when the container starts
model_pipe = model_fn()

@app.get("/ping")
def ping():
    heath_check = True if model_pipe else False
    status = "healthy" if heath_check else "unhealthy"
    status_code = 200 if heath_check else 503
    return Response(
        content=json.dumps({"status": status}),
        media_type="application/json",
        status_code=status_code
    )

@app.post("/invocations")
async def transcribe(file: UploadFile = File(...)):
    file_bytes = await file.read()
    audio_bytes = input_fn(file_bytes, file.content_type, 16000)
    transcription = predict_fn(audio_bytes, model_pipe)
    return output_fn(transcription)
