# Hurdles Time Prediction Model - Integration Proposal

# Approach: Add to Existing Backend

Integrate ML model as a new service within current FastAPI backend so no new infrastructure is needed


# 1. Where the Model Would Be Stored

**routes/**
- `prediction.py` - API endpoint for predictions

**services/**
- `ml/predictor.py` - prediction (loads models, runs predictions, returns results)
- `ml/preprocessing.py` - Feature preparation (transforms input data into model ready format)

**schemas/**
- `prediction.py` - Request/response validation (defines what valid prediction data looks like)

**core/**
- `ml_models/hurdles_110h_v1.pkl` - Trained model for men's 110h
- `ml_models/hurdles_100h_v1.pkl` - Trained model for women's 100h
- `ml_models/hurdles_400h_v1.pkl` - Trained model for 400h
- `ml_models/scaler_v1.pkl` - Feature scaler (normalizes input data)


* Why pkl files: only need to train and save once → model ready instantly (no retraining)


# 2. Deployment


The models get loaded once when the backend starts up and stay in memory. When a prediction request comes in, the model is already loaded and ready to respond instantly.


1. Backend starts → reads .pkl files from disk → loads models into memory
2. Models stay in memory while backend runs
3. Request comes in → model already loaded → predict instantly → return result
4. Backend restarts/redeploys → models reload from disk


- No changes to current deployment process
- Models deploy with backend code, included in Docker image
- No new servers, containers, or services needed
- Uses existing infrastructure

If we need to update the model:
- Replace .pkl file with new version
- Redeploy backend (like normal backend updates)
- New model loads automatically on startup

---

## 3. How It Fits in the Codebase

**Request flow:**

Request → `routes/prediction.py` → `services/ml/predictor.py` → model predicts → return result


# Integration:

**Routes** - Add new endpoint alongside existing routes
- `routes/prediction.py` handles prediction requests

**Services** - Add ML service alongside other services
- `services/ml/predictor.py` contains prediction logic

**Schemas** - Add validation for prediction data
- `schemas/prediction.py` validates requests (like other schemas validate their data)

**Core** - Store model files with other core resources
- `core/ml_models/*.pkl` loaded at startup



**Pros:**
- Uses existing backend structure
- No new infrastructure or services
- Fast to implement
- Models in memory means fast predictions 

**Cons:**
- Models use backend memory
- Model updates require backend redeploy