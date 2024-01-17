FROM python:3
ENV PYTHONUNBUFFERED 1


# Create code source code folder
RUN mkdir /src


# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip


# Install python packet
COPY docker/django/requirements.txt /
RUN pip install -r requirements.txt

COPY src/requirements.txt /
RUN pip install -r requirements.txt
