# WET-server

Build:

```
docker build -t glm-engine-api .
```

Run:

```
docker run -d --name glm-engine-api -p 80:80 --network glm-testing glm-engine-api
```

Dev environment:

```
conda create -n fastapi python=3.11
conda activate fastapi
pip install -r requirements.txt
pip install glm-py-0.0.1.tar.gz
```


Tests:

```
cd tests
python test.py
```
