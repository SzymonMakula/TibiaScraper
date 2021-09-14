FROM python:3.8.2
WORKDIR /home/bot
RUN apt update && apt install -y libffi-dev libnacl-dev python3-dev ffmpeg
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "discord_bot.py"]
