FROM python:3.9-slim-buster

WORKDIR /src

ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_HOST=final-project-sc
ENV POSTGRES_DB=final-project-sc
ENV POSTGRES_PORT=5432

COPY . .
RUN python3.9 -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "flask", "--app", "app/app.py", "--debug", "run", "--host=0.0.0.0" ]