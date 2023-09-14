FROM jmad1v07/wet-glm 

RUN apt-get -y update && apt-get -y upgrade

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
RUN pip3 install pip install -i https://test.pypi.org/simple/ glm-py==0.0.1

WORKDIR /glm-engine

COPY ./app /glm-engine/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--loop", "asyncio", "--port", "80"]