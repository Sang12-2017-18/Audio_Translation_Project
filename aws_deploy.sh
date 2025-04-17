#!/bin/bash
# This script deploys a Docker container to AWS ECR using the AWS CLI.
# It builds the Docker image, pushes it to Amazon ECR.
# Usage: ./aws_deploy.sh <AWS_REGION> <ECR_REPOSITORY_NAME> <DOCKER_CONTAINER_NAME>
# Ensure the script is run with the correct number of arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <AWS_REGION> <ECR_REPOSITORY_NAME> <DOCKER_CONTAINER_NAME>"
    exit 1
fi
# Assign command line arguments to variables
AWS_REGION=$1
ECR_REPOSITORY_NAME=$2
DOCKER_CONTAINER_NAME=$3
# Set the AWS region
export AWS_REGION=$AWS_REGION
# Set the AWS CLI profile (optional)
# export AWS_PROFILE=your-profile-name
# Get the account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create AWS ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION || \
aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION
# Authenticate Docker to the ECR registry
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
# Build the Docker image
docker build --platform="linux/amd64" -t $DOCKER_CONTAINER_NAME .
# Tag the Docker image
docker tag $DOCKER_CONTAINER_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest
# Push the Docker image to ECR
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest

