FROM python:3.13

WORKDIR /app

# Создаем необходимые директории
RUN mkdir -p /app/src/images

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Копируем код
COPY . .

CMD ["python", "src/main.py"]