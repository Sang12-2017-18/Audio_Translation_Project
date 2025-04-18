# Bengali Speech-to-Text ASR using Hugging Face + SageMaker
- A project using Hugging Face to deploy a Bengali ASR model on AWS SageMaker.
- The purpose: to help me subtitle Bengali Movies.
- The model used is a fine-tuned version of Whisper (bengaliAI/tugstugi_bengaliai-asr_whisper-medium).
- Deployment was done on AWS SageMaker, by creating a container on ECR.
- Docker was used to create the container.
- A frontend was created using Streamlit and FastAPI to interact with the model.
- Audio processing (conversion to mono and 16kHz) was done using the `librosa` library.

## Prerequisites
- AWS account. 
- An IAM user with access to SageMaker (AmazonSageMakerFullAccess) and ECR (AmazonEC2ContainerRegistryPowerUser), and a role with full access to Sagemaker (AmazonSageMakerFullAccess).
- Docker installed on your local machine.
- Python 3.11.6 installed on your local machine.
- AWS CLI installed on your local machine.

## Python version used for the project
```bash
$ python --version
Python 3.11.6
```

## Libraries used
- project_code/requirements.txt: List libraries required for the ML model.
- frontend_code/requirements.txt: List libraries required for the frontend.
- project_code/torch_reqs.txt: Torch version for the model.

## Getting the model to execution
- Step 1: Clone the repository, and run the save_model.py file to save the model.
- Step 2: To deploy the aws model, create a docker image using the Dockerfile provided in the project_code directory. These steps are mentioned in detail in the aws_deploy.sh file. You can execute the file as given in the comments in the file.
- Step 3: Once that file is executed, the model image will be created in AWS ECR. To deploy the model on sagemaker, execute the sagemaker_deploy.py file. The image_uri is the value you supply to docker push command in the aws_deploy.sh file. The sagemaker_deploy.py file will create a sagemaker endpoint for you to use.
- Step 4: Now the model is deployed on AWS. You can use the frontend code to interact with the model. The frontend code is in the frontend_code directory. You can run the app using the command below.
```bash
$ streamlit run app.py
``` 
To also run the fastapi app, which is the backend for streamlit; you can run the command below.
```bash
$ uvicorn frontend_code/api:app --reload --port 8001
```
The port for the frontend_code/api is 8001, and should be the same as the port mentioned in API_BASE (frontend_code/constants.py).
- Step 5: The frontend code will run on port 8501, and the fastapi app will run on port 8001. You can upload the audio file, or download YouTube audio, and do the transcription and translation.

## Demo Video
[![Bengali ASR Demo Video](https://raw.githubusercontent.com/Sang12-2017-18/Audio_Translation_Project/main/media/asr_demo_thumbnail.png)](https://raw.githubusercontent.com/Sang12-2017-18/Audio_Translation_Project/main/media/Translation_live_video.mov)

## Tech Stack
Hugging Face 🤗, Whisper, FastAPI, Docker, AWS SageMaker, AWS ECR, Streamlit, FastAPI, Librosa, yt-dlp, AWS CloudWatch,
