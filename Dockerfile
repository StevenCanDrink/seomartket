FROM python:3.12.11-alpine3.22

WORKDIR /app

# Use apk instead of apt-get for Alpine Linux
RUN apk add --no-cache \
    glib \
    libsm \
    libxrender \
    libxext \
    mesa \
    glu \
    ttf-dejavu \
    fontconfig \
    pango \
    cairo \
    gdk-pixbuf

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Changed from /code to /app to match WORKDIR
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]