from fastapi import FastAPI, Request
from transformers import pipeline
import uvicorn
import numpy as np  # Force numpy import check at startup

app = FastAPI()

# Multilingual (Indonesian + English) review sentiment.
# DistilBERT student distilled from zero-shot — 3 classes: positive / neutral / negative.
classifier = pipeline(
    "text-classification",
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    top_k=None
)


def _capitalize_labels(obj):
    """n8n compares labels against title case ('Positive'/'Negative'/'Neutral'),
    while this model returns lowercase. Normalize in place, preserving response shape."""
    if isinstance(obj, dict):
        if isinstance(obj.get("label"), str):
            obj["label"] = obj["label"].capitalize()
        for v in obj.values():
            _capitalize_labels(v)
    elif isinstance(obj, list):
        for v in obj:
            _capitalize_labels(v)
    return obj


@app.post("/predict")
async def predict(request: Request):
    body = await request.json()
    inputs = body.get("inputs", "")
    if not inputs:
        return []
    return _capitalize_labels(classifier(inputs))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
