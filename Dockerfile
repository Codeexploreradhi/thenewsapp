FROM heroku/heroku:16
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app
RUN apt-get update
RUN apt-get install -y libpng-dev python-subprocess32 python-dev python-matplotlib xvfb
RUN wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
RUN python /tmp/get-pip.py
WORKDIR /app
ADD . /app/

RUN pip install -r model.txt
RUN pip install -r requirements.txt
CMD sh run_app.sh
