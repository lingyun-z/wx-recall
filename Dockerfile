FROM python:3.6
WORKDIR /app
COPY main.py app/main.py
RUN pip install -r requirements.txt
CMD ["sh", "-c", "exec python main.py"]
