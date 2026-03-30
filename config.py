import os

class Config:
    # --- Database & Security ---
    SECRET_KEY = "insightstream_secret_key"
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'Lak@2408'
    MYSQL_DB = 'insightstream_db'

    # --- Paths ---
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    MODELS_PATH = os.path.join(BASE_DIR, 'notebooks', 'models')

    # Forecasting Metadata
    FORECAST_R2_SCORE = 0.8994
    FORECAST_MAE = 1.4608
    
    # Auditor / Anomaly Metadata
    AUDIT_CONTAMINATION = 0.03 
    
    # Spend Ratios (DNA of your training data)
    DEFAULT_RATIOS = {
        'TV': 0.45,
        'Radio': 0.35,
        'Newspaper': 0.20
    }