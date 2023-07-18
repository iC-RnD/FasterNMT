FROM pytorch/pytorch:1.9.1-cuda11.1-cudnn8-devel

RUN pip install --upgrade pip
WORKDIR /app

# RUN apt-get update && apt-get install build-essential cmake git -y

# RUN pip install torch==1.9.1+cu111 torchvision==0.10.1+cu111 torchaudio==0.9.1 -f https://download.pytorch.org/whl/torch_stable.html

COPY reqs.txt /app/

RUN pip install -r reqs.txt

RUN python -m nltk.downloader punkt
RUN python -c "import nltk;nltk.download('punkt')"
COPY ./models /app/models
COPY ./inference.py /app/
COPY ./service.py /app/
COPY ./main.py /app/
COPY ./config.py /app/
COPY ./Sentence_spliting.py /app/



RUN rm -r ~/.cache/pip/*

EXPOSE 8000

CMD ["python", "main.py"]
