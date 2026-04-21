from fastapi import FastAPI

app = FastAPI(title="CodeGen Analyst Agent")

@app.get("/")
def root():
    return {"message": "AI Analyst Agent is running 🚀"}