FROM python:3.11-slim

WORKDIR /app

# install dependencies first (caches this step)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the app
COPY . .

# make start script executable
RUN chmod +x start.sh

EXPOSE 8501

CMD ["./start.sh"]
