FROM public.ecr.aws/lambda/python:3.11

LABEL maintainer="CDK Lambda Django"

RUN pip3 install --no-cache-dir --upgrade pip

# Copy function code
COPY . .

# Install python dependencies
RUN pip install -r requirements-cdk.txt
RUN pip install -r requirements.txt

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "handler.handler" ]
