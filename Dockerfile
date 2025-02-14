# Pip dependency `mariadb` causing problems:
# https://stackoverflow.com/questions/73350980/python-mariadb-library-and-his-connector-inside-a-docker-container
FROM python:3.13.2-bookworm

WORKDIR /app

RUN apt update && \
    apt install -yq apt-utils && \
    apt install -yq procps && \
    apt install -yq vim && \
    apt install -yq libmariadb3 libmariadb-dev
RUN rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
