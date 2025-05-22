############################
# kafka-producer/Dockerfile
############################
FROM python:3.11-slim-bookworm AS builder
WORKDIR /build
COPY requirements.txt .
# install straight into /usr/local (default python search path)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM gcr.io/distroless/python3-debian12
USER nonroot
WORKDIR /app
# bring the libs across
COPY --from=builder /install /usr/local
COPY kafka-producer/ .
ENV PYTHONPATH="/usr/local/lib/python3.11/site-packages"
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "main.py"]
