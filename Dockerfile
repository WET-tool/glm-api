FROM jmad1v07/wet-glm 

RUN apt-get -y update && apt-get -y upgrade

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY glm-py-0.0.2.tar.gz /tmp/glm-py-0.0.2.tar.gz
RUN pip3 install /tmp/glm-py-0.0.2.tar.gz

WORKDIR /glm-engine

COPY ./app /glm-engine/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--loop", "asyncio", "--port", "80"]