FROM python:3.8-slim

LABEL base_image="python:3.8-slim"
LABEL about.home="https://github.com/Clinical-Genomics/cg_lims"
LABEL about.tags="NIPT,statistics,Non Invasive Prenatal Test,python"


ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=1
ENV GUNICORN_BIND="0.0.0.0:8000"
ENV GUNICORN_TIMEOUT=400
ENV BASEURI="https://clinical-lims-stage.scilifelab.se"
ENV HOST="clinical-lims-stage.scilifelab.se"
ENV USERNAME="apiuser"
ENV PASSWORD="??"
ENV CG_URL="https://clinical-api.scilifelab.se/api/v1"
ENV CG_LIMS_HOST="localhost"
ENV CG_LIMS_PORT=8000

EXPOSE 8000

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install app requirements
RUN pip install -r requirements.txt

# Install app
RUN pip install -e .

CMD gunicorn \
    --workers=$GUNICORN_WORKERS \
    --bind=$GUNICORN_BIND  \
    --threads=$GUNICORN_THREADS \
    --timeout=$GUNICORN_TIMEOUT \
    --proxy-protocol \
    --forwarded-allow-ips="10.0.2.100,127.0.0.1" \
    --log-syslog \
    --access-logfile - \
    --log-level="debug" \
    --worker-class=uvicorn.workers.UvicornWorker \
    cg_lims.app.api.api_v1.api:app