FROM python:3.8-slim-buster

COPY pip.conf /etc/pip.conf
COPY ./requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app/
CMD ["python", "/app/it_jackpot_bot.py"]
