# InsightStream: Automated Financial Intelligence & Predictive Forecasting

**InsightStream** is an end-to-end financial intelligence and predictive analytics platform engineered specifically for the Small and Medium Business (SMB) landscape. In an era of "Big Data," most enterprises are overwhelmed by transactional volume but lack the computational intelligence to forecast future trends. InsightStream functions as a **Digital Financial Co-Pilot**, utilizing **Supervised Machine Learning** to convert dormant accounting data into active business strategy.

## 🚀 Key Features

* **AI Digital Auditor:** An automated risk-assessment engine that scans transaction patterns against historical baselines to flag anomalies, duplicate billings, and statistical outliers, reducing manual accounting error by up to 90%.
* **Predictive Growth Simulator:** A interactive "What-If" sandbox using **Linear Regression** and a custom **Efficiency Scaling Factor** to forecast 6-month revenue trajectories based on adjustable marketing spend.
* **Intelligent ETL Pipeline:** A zero-config data ingestion module powered by **Pandas** that identifies "Date," "Amount," and "Category" from diverse CSV structures, standardizing raw data for AI processing.
* **Interactive KPI Dashboard:** High-performance visualization suite built with **Chart.js**, translating high-dimensional financial data into real-time, scannable visual insights.
* **Secure Data Architecture:** Enterprise-grade security implementing **PBKDF2 password hashing** via Werkzeug and a relational **MySQL** structure for isolated user data integrity.

## 🛠️ Tech Stack

* **Backend:** Python 3.8+, Flask Framework
* **Machine Learning:** Scikit-Learn (Linear Regression, Outlier Detection), Joblib
* **Database:** MySQL 8.0+ (ACID Compliant)
* **Frontend:** HTML5, Tailwind CSS, Chart.js, Jinja2
* **Data Science:** Pandas, NumPy

## 📊 Mathematical Foundation

The core predictive engine utilizes a weighted linear relationship. While the base model uses **Linear Regression** to determine a trend line, we apply a **Business Efficiency Coefficient ($C_e$)** to personalize the output based on a specific firm's historical performance:

$$Revenue_{predicted} = (\beta_0 + \beta_1 \cdot \text{Marketing Spend}) \cdot C_e$$

* **$\beta_0$**: Baseline revenue without marketing investment.
* **$\beta_1$**: Growth coefficient derived from historical data training.
* **$C_e$**: The ratio of Current Efficiency vs. Industry/Historical Baseline.

## 📂 System Architecture

* **Module 1: Authentication & Identity** – Secure session management and hashed user credentials.
* **Module 2: Data Ingestion (ETL)** – Flexible column-mapping algorithm for standardized data cleaning.
* **Module 3: AI Digital Auditor** – Pattern recognition engine for transaction auditing.
* **Module 4: Predictive Simulator** – Scenario-based forecasting engine with interactive UI controls.

## 💻 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/InsightStream.git](https://github.com/yourusername/InsightStream.git)
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Database Configuration:**
    * Initialize a MySQL instance and run the provided schema scripts.
    * Configure the connection string in the environment variables.
4.  **Launch Platform:**
    ```bash
    python app.py
    ```

## 📜 Academic Credits

This project was developed as a Major Project in partial fulfillment of the requirements for the **Bachelor of Computer Applications (BCA)** degree at **Guru Gobind Singh Indraprastha University** (New Delhi).

