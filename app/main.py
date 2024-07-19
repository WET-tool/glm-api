from fastapi import FastAPI
from fastapi import UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse

from starlette.background import BackgroundTask

import os
import shutil
import json

import numpy as np

from glmpy import simulation as sim

import app.lake_balance.lake_balance as lake_balance

description = """
API for the General Lake Model (GLM)
"""

tags_metadata = [
    {
        "name": "inputs_files",
        "description": "Run GLM simulation and receive all outputs (including netcdf) in a zip file.",
    },
    {
        "name": "inputs_csv_files",
        "description": "Run GLM simulation and receive all CSV outputs (excluding netcdf) in a zip file.",
    },
    {
        "name": "inputs_json_files",
        "description": "Run GLM simulation and receive all CSV outputs converted to JSON in a zip file.",
    },
    {
        "name": "inputs_json",
        "description": "Run GLM simulation and receive all CSV outputs converted to JSON.",
    },
    {
        "name": "inputs_lake_sim_basic",
        "description": "Run a simple lake simulation using logic based off DAMCAT v5.",
    },
]

app = FastAPI(
    title="GLM API",
    description=description,
    openapi_tags=tags_metadata
)


def cleanup_files(inputs_dir):
    shutil.rmtree(str(inputs_dir))


@app.post("/inputs_files", tags=["inputs_files"])
def run_glm(files: list[UploadFile], out_dir: str = Form()):
    # run simulation
    glm_run = sim.GlmSim(files, True, "/inputs")
    inputs_dir = glm_run.prepare_inputs()
    glm_run.glm_run(inputs_dir, "/glm/glm")

    # process outputs
    outputs_dir = os.path.join(inputs_dir, out_dir)
    glm_process = sim.GlmPostProcessor(outputs_dir)
    files_zip_path = glm_process.zip_outputs()

    return FileResponse(files_zip_path)


@app.post("/inputs_csv_files", tags=["inputs_csv_files"])
def run_glm_csv_files(files: list[UploadFile], out_dir: str = Form()):
    # run simulation
    glm_run = sim.GlmSim(files, True, "/inputs")
    inputs_dir = glm_run.prepare_inputs()
    glm_run.glm_run(inputs_dir, "/glm/glm")

    # process outputs
    outputs_dir = os.path.join(inputs_dir, out_dir)
    glm_process = sim.GlmPostProcessor(outputs_dir)
    csv_zip_path = glm_process.zip_csvs()

    return FileResponse(csv_zip_path)


@app.post("/inputs_json_files", tags=["inputs_json_files"])
def run_glm_json_files(files: list[UploadFile], out_dir: str = Form()):
    # run simulation
    glm_run = sim.GlmSim(files, True, "/inputs")
    inputs_dir = glm_run.prepare_inputs()
    glm_run.glm_run(inputs_dir, "/glm/glm")

    # process outputs
    outputs_dir = os.path.join(inputs_dir, out_dir)
    glm_process = sim.GlmPostProcessor(outputs_dir)
    glm_process.csv_to_json_files()
    json_zip_path = glm_process.zip_json()

    return FileResponse(json_zip_path)


@app.post("/inputs_json", tags=["inputs_json"])
def run_glm_json(
    files: list[UploadFile],
    csv_lake_fname: str = Form(),
    variables: list = Form(),
    out_dir: str = Form()
):  
    # run simulation
    glm_run = sim.GlmSim(files, True, "/inputs")
    inputs_dir = glm_run.prepare_inputs()
    glm_run.glm_run(inputs_dir, "/glm/glm")

    # process outputs
    outputs_dir = os.path.join(inputs_dir, out_dir)
    glm_process = sim.GlmPostProcessor(outputs_dir)
    json_output = glm_process.csv_to_json(csv_lake_fname, variables)

    return JSONResponse(json_output)


@app.post("/inputs_lake_sim_basic", tags=["inputs_lake_sim_basic"])
def run_lake_sim_basic(
    files: list[UploadFile],
    leaky_lake: bool = Form(),
    evap_factor: float = Form(),
):
    # process input files
    for f in files:
        # see NumPy load() docs - NumPy load() expects a filelike object with a read method
        # the NumPy load() function will handle calling read()
        if f.filename == "lake_sim_inputs.npy":
            tmp_met = np.load(f.file)
        
        if f.filename == "lake_config.json":
            lake_config = json.loads(f.file.read()) 

    basic_sim_outputs = lake_balance.daily_sim(tmp_met, lake_config, leaky_lake, evap_factor)   

    return JSONResponse(basic_sim_outputs)