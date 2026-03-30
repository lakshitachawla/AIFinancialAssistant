import os
import pandas as pd
import numpy as np
import joblib
import mysql.connector
from datetime import datetime
from flask import Flask, make_response, render_template, session, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['SESSION_COOKIE_NAME'] = 'insightstream_session' 
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = None
app.config['SESSION_USE_SIGNER'] = False

# --- DATABASE CONNECTION ---
def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )

# --- LOGIN MANAGER ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'
login_manager.login_message_category = 'error'
login_manager.login_message = None

class User(UserMixin):
    def __init__(self, user_id, email, business_name):
        self.id = str(user_id) 
        self.email = email
        self.business_name = business_name

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    u = cursor.fetchone()
    conn.close()
    if u:
        return User(u['id'], u['email'], u['business_name'])
    return None

# --- ML ASSET LOADING ---
def load_ml_models():
    try:
        return {
            "forecaster": joblib.load(os.path.join(Config.MODELS_PATH, "forecaster.pkl")),
            "auditor": joblib.load(os.path.join(Config.MODELS_PATH, "auditor.pkl")),
            "ratios": Config.DEFAULT_RATIOS
        }
    except:
        print("CRITICAL: ML Models not found in notebooks/models/")
        return None

ML_MODELS = load_ml_models()

# 1. LANDING PAGE
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# 2. AUTH UI CONTAINER
@app.route('/auth', methods=['GET'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('user_auth.html')

# 3. LOGIN ROUTE
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Handle GET requests (user just arriving at the page)
    if request.method == 'GET':
        return redirect(url_for('auth'))

    # 2. Handle POST requests (user submitting the form)
    if request.method == 'POST':
        session.pop('_flashes', None) 
        
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for('auth'))

        # Move Database logic INSIDE the POST block
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and check_password_hash(user_data['password'], password):
            user_obj = User(user_data['id'], user_data['email'], user_data['business_name'])
            # Flask-Login handles the session creation here
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('auth'))

# 4. REGISTER PROCESSOR 
@app.route('/register', methods=['POST','GET'])
def register():
    business_name = request.form.get('business_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')

    if not all([business_name, email, password]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for('auth'))

    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (business_name, email, phone, password) 
            VALUES (%s, %s, %s, %s)
        """, (business_name, email, phone, hashed_pw))
        conn.commit()
        flash("Account created! Please sign in.", "success")
    except Exception as e:
        print(f"REGISTER ERROR: {e}")
        flash("Email already exists. Try logging in.", "error")
    finally:
        conn.close()
    
    return redirect(url_for('auth'))

# 5. LOGOUT
@app.route('/logout')
@login_required 
def logout():
    logout_user()
    session.clear()
    response = make_response(redirect(url_for('index')))
    response.set_cookie('insightstream_session', '', expires=0)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    flash("You have been logged out successfully.", "info")
    return response

# --- ROUTES: CORE PLATFORM ---
# DASHBOARD ROUTE
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date ASC", (current_user.id,))
        txs = cursor.fetchall()

        # KPI Variables
        total_revenue = 0.0
        total_units = 0.0
        mkt_spend = 0.0
        anomaly_count = 0
        category_dist = {}
        
        # Chart Data
        allLabels, allRevData, allQtyData = [], [], []

        for t in txs:
            amt = float(t.get('amount') or 0)
            qty = float(t.get('quantity') or 0)
            cat = str(t.get('category') or "Other").strip().title()
            cat_l = cat.lower()

            # Date Processing
            date_str = t['transaction_date'].strftime('%Y-%m-%d') if t['transaction_date'] else "No Date"
            allLabels.append(date_str)
            
            # 1. Total Units
            total_units += qty
            
            # 2. Revenue & Line Chart Data
            if "revenue" in cat_l or "sale" in cat_l:
                rev_val = abs(amt)
                total_revenue += rev_val
                allRevData.append(rev_val)
            else:
                allRevData.append(0) 
            
            # 3. Efficiency ROI Calculations
            if any(kw in cat_l for kw in ['mkt', 'marketing', 'ads', 'promo']):
                mkt_spend += abs(amt)

            # 4. Anomalies
            if t.get('is_anomaly') == 1:
                anomaly_count += 1
            
            # 5. Quantity Data for Chart
            allQtyData.append(qty)

            # 6. Doughnut Chart Aggregation
            category_dist[cat] = category_dist.get(cat, 0) + abs(amt)

        # 7. Final KPI Calculations
        efficiency = (total_revenue / mkt_spend) if mkt_spend > 0 else 0
        
        kpis = {
            "total_revenue": total_revenue,
            "total_units": int(total_units),
            "efficiency": round(efficiency, 1),
            "anomaly_count": anomaly_count,
            "category_dist": category_dist
        }

        return render_template('dashboard.html', 
                               kpis=kpis, 
                               allLabels=allLabels, 
                               allRevData=allRevData, 
                               allQtyData=allQtyData)

    except Exception as e:
        print(f"Dashboard Error: {e}")
        flash("Could not load dashboard data.", "error")
        return redirect(url_for('index'))
    finally:
        conn.close()

# CSV UPLOAD ROUTE
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files.get('file')
    if not file: return redirect(url_for('dashboard'))
    
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower()

    # Column Mapping
    mapping = {'date':None, 'desc':None, 'amt':None, 'cat':None, 'qty':None}
    for col in df.columns:
        if 'date' in col: mapping['date'] = col
        if 'desc' in col or 'item' in col: mapping['desc'] = col
        if 'amount' in col or 'price' in col: mapping['amt'] = col
        if 'cat' in col or 'type' in col: mapping['cat'] = col
        if 'quantity' in col or 'qty' in col or 'unit' in col: mapping['qty'] = col

    conn = get_db_connection()
    cursor = conn.cursor()
    
    for i, row in df.iterrows():
        raw_amt = float(row[mapping['amt']])
        raw_qty = float(row[mapping['qty']]) if mapping['qty'] else 1.0
        cat_name = str(row[mapping['cat']]).lower()
        
        # Categorization logic
        is_mkt = any(kw in cat_name for kw in ['mkt', 'marketing', 'ads', 'promo'])
        is_rev = any(kw in cat_name for kw in ['sale', 'revenue', 'income', 'upi'])
        
        # Standardizing signs: Expenses negative, Revenue positive
        amt = -abs(raw_amt) if (is_mkt or 'spend' in cat_name) else abs(raw_amt)

        # --- AUDITOR MODEL ALIGNMENT ---
        mkt_val = abs(amt) if is_mkt else 0
        rev_val = abs(amt) if is_rev else 0
        is_dup = 1 if df.duplicated().iloc[i] else 0
        
        # Prepare DataFrame with feature names from your notebook
        audit_df = pd.DataFrame([{"marketing_spend": mkt_val, "revenue": rev_val, "is_duplicate": is_dup}])
        
        try:
            # Model prediction 
            is_anomaly = 1 if (ML_MODELS['auditor'].predict(audit_df)[0] == -1 or abs(amt) > 10000) else 0
        except:
            is_anomaly = 0

        cursor.execute("""INSERT INTO transactions 
            (user_id, transaction_date, description, category, quantity, amount, is_anomaly) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (current_user.id, row[mapping['date']], row[mapping['desc']], cat_name.title(), 
             raw_qty, amt, is_anomaly))
    
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# TRANSACTIONS ROUTE
@app.route('/transactions')
@login_required
def transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date DESC", (current_user.id,))
    txs = cursor.fetchall()
    conn.close()
    return render_template('transactions.html', transactions=txs)

# FUTURE PLANNER ROUTE
@app.route('/planner')
@login_required
def planner():
    return render_template('planner.html')

# SIMULATION FUNCTION ROUTE
@app.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    data = request.json
    budget = float(data.get('budget', 0))
    multiplier = float(data.get('multiplier', 1.0))
    scenario_name = data.get('scenario_name', f"Scenario_{datetime.now().strftime('%Y%m%d_%H%M')}")
    
    # 1. Model Mapping
    ratios = {'TV': 0.7, 'Radio': 0.2, 'Newspaper': 0.1}
    X_sim = pd.DataFrame([[
        budget * ratios['TV'],
        budget * ratios['Radio'],
        budget * ratios['Newspaper']
    ]], columns=['tv', 'radio', 'newspaper'])
    
    # 2. Get Raw Forecast from trained model
    raw_forecast = ML_MODELS['forecaster'].predict(X_sim)[0]
    
    # 3. Clean Efficiency Calculation 
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN category LIKE '%%revenue%%' OR category LIKE '%%sale%%' THEN amount ELSE 0 END) as rev,
            SUM(CASE WHEN (category LIKE '%%mkt%%' OR category LIKE '%%marketing%%') AND is_anomaly = 0 THEN ABS(amount) ELSE 0 END) as spend
        FROM transactions WHERE user_id = %s
    """, (current_user.id,))
    
    row = cursor.fetchone()
    user_rev = float(row[0] or 0)
    user_spend = float(row[1] or 1) 
    
    user_eff = user_rev / user_spend
    training_baseline_eff = 0.07 
    scale_factor = user_eff / training_baseline_eff
    
    final_pred = float(raw_forecast * scale_factor * multiplier)
    
    # 4. DATABASE INSERT
    try:
        query = """
            INSERT INTO forecasts 
            (user_id, forecast_date, predicted_revenue, scenario_name, budget_allocated, strategy_multiplier) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            current_user.id, 
            datetime.now().date(), 
            round(final_pred, 2), 
            scenario_name, 
            budget, 
            multiplier
        )
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        print(f"SQL Error: {e}")
    finally:
        conn.close()

    # 5. Trajectory and Historical Baseline for Line Chart
    trajectory = [round(final_pred * (1 + (i * 0.05)), 2) for i in range(6)]
    baseline_val = round(user_rev / 6, 2) if user_rev > 0 else 0
    baseline = [baseline_val] * 6 

    return jsonify({
        "forecast": round(final_pred, 2),
        "trajectory": trajectory,
        "baseline": baseline
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)