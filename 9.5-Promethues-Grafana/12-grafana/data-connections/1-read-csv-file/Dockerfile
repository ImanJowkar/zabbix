FROM hub.hamdocker.ir/python:3.9-alpine

WORKDIR /app
RUN mkdir -p /app/data

COPY fruit_data_generator.py .


CMD ["python", "fruit_data_generator.py"]
