FROM python:3.9-slim

WORKDIR /app

# Install CAN support
RUN apt-get update && \
    apt-get install -y python3-can && \
    pip install kuksa-client && \
    apt-get clean

COPY . .

CMD ["python3", "vehicle_speed_service.py", "--broker", "localhost", "--port", "55555"]

