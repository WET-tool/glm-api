FROM jmad1v07/wet-glm 

RUN apt-get -y update && apt-get -y upgrade

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /glm-engine

COPY glm-py-0.0.1.tar.gz /glm-engine/glm-py-0.0.1.tar.gz
RUN pip3 install /glm-engine/glm-py-0.0.1.tar.gz

COPY ./app /glm-engine/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--loop", "asyncio", "--port", "80"]