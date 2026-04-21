import os

from fastapi import FastAPI, HTTPException
import pandas as pd
from app.agent.agentConfig import code_evaluation, code_generation, df_schema
from app.modelconfig import PROVIDER, get_model_name, extract_json


app = FastAPI()

QUESTION_2 = """Using only vehicles with model year 2017, compute for each state:
  - the average price of automatic-transmission vehicles
  - the overall average price of all vehicles in that state

  Calculate the percentage deviation of automatic vehicles from the state average and return the single state with the maximum absolute deviation, along with the deviation value."""
DATA_PATH = os.getenv("DATA_FILE", "data/datafile.csv")

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
    data_path = os.getenv("DATA_FILE", "data/datafile.csv")
    df = pd.read_csv(data_path)
    return df