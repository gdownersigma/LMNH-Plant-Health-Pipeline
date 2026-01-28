FROM python:latest

WORKDIR /app

COPY pipeline_requirements.txt .
RUN pip install -r pipeline_requirements.txt

COPY extract/extract.py extract/

COPY transform/transform_botanist.py transform/
COPY transform/transform_plants.py transform/
COPY transform/transform_origin.py transform/
COPY transform/transform_readings.py transform/

COPY load/load_botanist.py load/
COPY load/load_plant.py load/
COPY load/load_origin.py load/
COPY load/load_plant_readings.py load/

COPY pipeline.py .

CMD ["python", "pipeline.py"]