FROM python:3.8

ENV DockerHOME=/app/

RUN mkdir -p $DockerHOME

ENV FLASK_APP=core/server.py

WORKDIR $DockerHOME

COPY . $DockerHOME

RUN pip install -r requirements.txt

RUN if [ -f core/store.sqlite3 ]; then rm core/store.sqlite3; fi

RUN flask db upgrade -d core/migrations/

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
