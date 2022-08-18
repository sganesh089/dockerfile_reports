FROM python:3

WORKDIR /usr/src/app

ADD . / ./

RUN apt-get update

RUN pip install --no-cache-dir -r requirements.txt 

RUN chmod a+x ./run.sh

CMD /bin/bash -c './run.sh; /bin/bash'
