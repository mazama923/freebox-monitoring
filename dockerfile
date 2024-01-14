FROM python:3.9.18-slim
WORKDIR /app
COPY ./app /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "main.py"]