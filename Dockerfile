# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

EXPOSE 5003

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN [ "python", "-c", "import nltk; nltk.download('wordnet', download_dir='/usr/local/nltk_data')" ]
RUN [ "python", "-c", "import nltk; nltk.download('punkt', download_dir='/usr/local/nltk_data')" ]
RUN [ "python", "-c", "import nltk; nltk.download('averaged_perceptron_tagger', download_dir='/usr/local/nltk_data')" ]

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:5003", "app:app"]
