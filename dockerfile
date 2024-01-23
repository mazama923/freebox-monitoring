FROM python:slim
WORKDIR /app
COPY ./app /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "main.py"]