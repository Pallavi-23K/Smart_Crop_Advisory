# backend.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import joblib
import uvicorn

# ---------- Initialize FastAPI ----------
app = FastAPI(title="Crop Advisory API")

# Allow CORS (so frontend can access backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for production, set your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Load model & label encoder ----------
model_file = "plant_disease_model.pkl"
label_file = "label_encoder.pkl"

model = joblib.load(model_file)
le = joblib.load(label_file)

# ---------- Feature extraction ----------
def extract_features(image):
    image = cv2.resize(image, (128, 128))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0,1,2], None, [8,8,8], [0,180,0,256,0,256])
    cv2.normalize(hist, hist)
    return hist.flatten()

# ---------- API Endpoint ----------
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        return {"disease": "Error: could not read image"}
    
    features = extract_features(image).reshape(1, -1)
    prediction = model.predict(features)
    disease_name = le.inverse_transform(prediction)[0]
    
    return {"disease": disease_name}

# ---------- Run Server ----------
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
