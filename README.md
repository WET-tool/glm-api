# GLM API

A FastAPI interface to the General Lake Model or a simple water balance model adapted from DAMCAT logic. 

The FastAPI application publishes the following endpoints:

* `inputs_files`: Run GLM simulation and receive all outputs (including netcdf) in a zip file.
* `inputs_csv_files`: Run GLM simulation and receive all CSV outputs (excluding netcdf) in a zip file.
* `inputs_json_files`: Run GLM simulation and receive all CSV outputs converted to JSON in a zip file.
* `inputs_json`: Run GLM simulation and receive all CSV outputs converted to JSON.
* `inputs_dam_sim_basic`: Run a simple farm dam simulation using logic based off DAMCAT v5.

## Deploy

Deployment is via Docker.

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
pip install glm-py-0.0.2.tar.gz
```

