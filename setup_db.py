import mysql.connector
from config import Config

def create_database():
    conn = None
    cursor = None

    try:
        # Connection to MySQL Server
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        cursor = conn.cursor()

        # Creating Database 
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}`")
        cursor.execute(f"USE `{Config.MYSQL_DB}`")


        # Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                business_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Transactions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                transaction_date DATE,
                description TEXT,
                category VARCHAR(100),
                quantity FLOAT,
                amount FLOAT,
                is_anomaly TINYINT(1) DEFAULT 0,
                risk_score FLOAT DEFAULT 0.0,
                CONSTRAINT fk_transactions_user
                    FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        # Forecasts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            forecast_date DATE NOT NULL,
            predicted_revenue FLOAT NOT NULL,
            scenario_name VARCHAR(100),
            budget_allocated FLOAT DEFAULT 0.0,
            strategy_multiplier FLOAT DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_forecasts_user
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        print(f"Database `{Config.MYSQL_DB}` and tables created successfully.")

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()
