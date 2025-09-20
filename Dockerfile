# Используем официальный образ Python как базовый
FROM python:3.10

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /code

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код проекта в рабочую директорию
COPY . /code/

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска сервера, но она будет переопределена в docker-compose.yml
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]