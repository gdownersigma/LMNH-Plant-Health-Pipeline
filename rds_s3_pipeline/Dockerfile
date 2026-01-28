FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY export_to_parquet.py .

CMD [ "export_to_parquet.export_all_tables" ]