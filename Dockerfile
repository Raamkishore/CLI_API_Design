FROM python:3-alpine3.12
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN pip install -e my_cli
EXPOSE 4000
CMD ["python3", "my_cli/my_cli/main_file.py"]