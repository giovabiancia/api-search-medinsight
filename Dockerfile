FROM python:3.8-slim-buster
EXPOSE 5005

# ENVIRONMENT VARIABLES
ENV SECRET_KEY=c4d196f0463bd6a7489e2f2a2e4583b98bd8f9a5c711ee2a9b61969ef2d80ad1
ENV SQLALCHEMY_TRACK_MODIFICATIONS=True


# RUN COMMANDS
RUN apt -y update
RUN apt-get install -y nano
RUN python3.8 -m pip install --upgrade pip
# RUN python3 -m venv venv
# RUN . venv/bin/activate

# COPY CURRENT DIRECTORY DATA TO APP DIRECTORY IN THE CONTAINER IMAGE
COPY . /app

# SET WORKING DIRECTORY IN THE CONTAINER IMAGE
WORKDIR /app

# RUN COMMAND IN THE CONTAINER IMAGE
RUN pip install -r deploy.requirements.txt
RUN pip install gunicorn
RUN export FLASK_APP=app/
# RUN flask init-db # goes timeout

# SET ENTRYPOINT
ENTRYPOINT ["/usr/local/bin/gunicorn"]

# RUN APPLICATION COMMAND
CMD ["--config", "gunicorn-cfg.py", "wsgi:app"]
