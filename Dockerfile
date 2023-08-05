FROM python:3.10-slim
WORKDIR /src/StupidBoiV2
COPY . .
RUN pip install discord.py==2.2.2
RUN pip install PyNacl==1.3.0
RUN apt-get update && apt-get install ffmpeg -y
CMD ["python","./lib/StupidBoiV2.py"]