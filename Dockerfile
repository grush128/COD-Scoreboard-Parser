FROM python:3

RUN apt-get update -y && apt-get install -y libgl1-mesa-dev tesseract-ocr libtesseract-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY credentials.json .
COPY token.pickle .

ENTRYPOINT [ "python", "./parser.py" ]
