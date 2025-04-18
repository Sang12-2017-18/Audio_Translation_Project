from sagemaker.model import Model

role = "your-sagemaker-role" # Add ARN of AWS role here.

model = Model(
    image_uri="your-image-uri",  # Replace with your actual image URI
    role=role
)

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
)