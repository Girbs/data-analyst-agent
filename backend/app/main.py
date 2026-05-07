import os
import contextlib
import io
import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

try:
    from .agent.agentConfig import code_evaluation, code_generation, df_schema
    from .modelconfig import PROVIDER, get_model_name, extract_json
except ImportError:
    import sys

    backend_dir = Path(__file__).resolve().parents[1]
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from app.agent.agentConfig import code_evaluation, code_generation, df_schema
    from app.modelconfig import PROVIDER, get_model_name, extract_json


app = FastAPI()

# Allow CORS for local frontend dev server(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTION_2 = """Using only vehicles with model year 2017, compute for each state:
  - the average price of automatic-transmission vehicles
  - the overall average price of all vehicles in that state

  Calculate the percentage deviation of automatic vehicles from the state average and return the single state with the maximum absolute deviation, along with the deviation value."""
DATA_PATH = os.getenv(
        "DATA_FILE",
        str(Path(__file__).resolve().parents[1] / "data" / "datafile.csv"),
)

@app.get("/")
def root():
    schema = df_schema()
    try:
        soql_query = get_data()
        print("Data loaded successfully. Schema: ", soql_query)
        code = code_generation(DATA_PATH, schema, QUESTION_2)
        evaluation = code_evaluation(QUESTION_2, code, schema)
        print("evaluation**************", evaluation)
        print("Code********************", code)

        llm_result_3 = extract_json(evaluation)

        print(f"The score of the code is {llm_result_3['score']}")
        print(f"The rationale for the score provided is: {llm_result_3['rationale']}")
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model service is unavailable. "
                f"provider={PROVIDER}, model={get_model_name()}."
                f"Error: {exc}"
            ),
        ) from exc

    return {
       # "code": code,
        "evaluation": evaluation,
        "model": {"provider": PROVIDER, "name": get_model_name()},
    }

def get_data() -> pd.DataFrame:
    data_path = os.getenv(
        "DATA_FILE",
        str(Path(__file__).resolve().parents[1] / "data" / "datafile.csv"),
    )
    df = pd.read_csv(data_path)
    return df

def extract_json(llm_output):
  json_text = re.search(r"\{.*\}", llm_output, re.DOTALL).group()
  result = json.loads(json_text)
  return result


def execute_generated_code(code_str: str):
    cleaned_code = fix_llm_code(code_str)

    execution_globals = {
        "__builtins__": __builtins__,
        "pd": pd,
        "get_data": get_data,
    }
    execution_locals = {}
    stdout_buffer = io.StringIO()

    with contextlib.redirect_stdout(stdout_buffer):
        exec(cleaned_code, execution_globals, execution_locals)

    if "result" in execution_locals:
        return execution_locals["result"]

    stdout_value = stdout_buffer.getvalue().strip()
    if stdout_value:
        return stdout_value

    return None

@app.get("/chat")
def chat_with_data(question: str) -> str:
    df = get_data()
    schema = df_schema()
    code = code_generation(DATA_PATH, schema, question)
    evaluation = code_evaluation(question, fix_llm_code(code), schema)
    llm_result_3 = extract_json(evaluation)
    execution_result = execute_generated_code(code)

    return execution_result


def fix_llm_code(code_str: str) -> str:
    """
    Cleans and fixes common issues in LLM-generated Python code strings.
    """
    
    # Fix markdown hyperlinks like [pd.read](http://...) -> pd.read
    code_str = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', code_str)
    
    # Remove markdown code fences (```python ... ``` or ``` ... ```)
    code_str = re.sub(r'```(?:python)?\n?', '', code_str)
    
    # Remove any remaining backticks
    code_str = code_str.replace('`', '')
    
    # Strip leading/trailing whitespace
    code_str = code_str.strip()
    
    return code_str

