from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

model_name = "bengaliAI/tugstugi_bengaliai-asr_whisper-medium"
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)
processor = AutoProcessor.from_pretrained(model_name)

model.save_pretrained("./model/")
processor.save_pretrained("./model/")