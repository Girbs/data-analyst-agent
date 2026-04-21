from fastapi import FastAPI
import pandas as pd
from agentConfig import code_evaluation, code_generation, df_schema


app = FastAPI()

QUESTION_2 = "Car Ordered by Customer in 2023"

@app.get("/")
def root():
    schema = df_schema()
    try:
        soql_query = get_data()
        code = code_generation(DATA_PATH, schema, QUESTION_2)
        evaluation = code_evaluation(QUESTION_2, code, schema)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model service is unavailable. "
                f"provider={PROVIDER}, model={get_model_name()}. "
                f"Error: {exc}"
            ),
        ) from exc

    return {
        "soql_query": soql_query,
        "code": code,
        "evaluation": evaluation,
        "model": {"provider": PROVIDER, "name": get_model_name()},
    }

def get_data() -> pd.DataFrame:
    data_path = os.getenv("DATA_FILE", "data/datafile.csv")
    df = pd.read_csv(data_path)
    return df