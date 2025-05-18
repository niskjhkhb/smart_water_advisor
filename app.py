from flask import Flask, redirect, render_template, request, jsonify, session, url_for
import sqlite3
import joblib
import pandas as pd
model = joblib.load("water_usage_model2.pkl")


app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect('water.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and result[1] == password:
             session['username'] = username
             return redirect(url_for('submit_usage', user_id=id))
            
        else:
            return jsonify({"error": "Invalid username or password"}), 401
   
    return render_template('login.html') 


# --- DATABASE INIT ---
def init_db():
    conn = sqlite3.connect('water.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Water usage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS water_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            region TEXT NOT NULL,
            number_of_people INTEGER NOT NULL,
            actual_usage INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            predicted_usage INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


#register


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        conn = sqlite3.connect('water.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            return jsonify({"error": "Username already exists"}), 409
        finally:
            conn.close()

    return render_template('register.html')  # Render form on GET request
   



    

#login










#submitting the users input


@app.route('/submit_usage', methods=['GET', 'POST'])
def submit_usage():
    if request.method == 'POST':
        username = session.get("username")  # ✅ Get username from session
        if not username:
            return jsonify({"error": "User not logged in"}), 403
        
        if request.is_json:
            data = request.get_json()  # ✅ Handle JSON input
            region = data.get("region")
            number_of_people = data.get("number_of_people")
            actual_usage = data.get("actual_usage")
            month = data.get("month")
            year = data.get("year")
        else:
            # ✅ Handle form input
            region = request.form.get("region")
            number_of_people = request.form.get("number_of_people")
            actual_usage = request.form.get("actual_usage")
            month = request.form.get("month")
            year = request.form.get("year")
        
        conn = sqlite3.connect("water.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_record = cursor.fetchone()

        if not user_record:
            conn.close()
            return jsonify({"error": "User not found"}), 404  # ✅ Error handling if user doesn't exist

        user_id = user_record[0]  # ✅ Extract user_id from the database

        print("Fetched User ID:", user_id)

        # Debugging output to check received data
        print("Received Data:", user_id, region, number_of_people, actual_usage, month, year)

        if not all([user_id, region, number_of_people, actual_usage, month, year]):
            return jsonify({"error": "Missing fields"}), 400

        # Prepare input for model
        features = pd.DataFrame([{"region": region, "number_of_people": number_of_people}])
        
        try:
            predicted_usage = int(model.predict(features)[0])
        except Exception as e:
            return jsonify({"error": f"Model prediction failed: {str(e)}"}), 500

        # Store in DB
        conn = sqlite3.connect("water.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO water_usage 
            (user_id, region, number_of_people, actual_usage, month, year, predicted_usage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, region, number_of_people, actual_usage, month, year, predicted_usage))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard', user_id=user_id))


    return render_template('submit_usage.html')  # ✅ Show form on GET request

#fetch user usage history

@app.route('/usage_history/<int:user_id>', methods=['GET'])
def usage_history(user_id):
    conn = sqlite3.connect("water.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT region, number_of_people, actual_usage, month, year, predicted_usage
        FROM water_usage WHERE user_id = ?
    ''', (user_id,))
    records = cursor.fetchall()
    conn.close()

    usage_data = [{
        "region": r,
        "number_of_people": n,
        "actual_usage": a,
        "month": m,
        "year": y,
        "predicted_usage": p
    } for r, n, a, m, y, p in records]

    return jsonify(usage_data), 200


@app.route('/dashboard/<int:user_id>', methods=['GET'])
def dashboard(user_id):
    conn = sqlite3.connect("water.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT region, number_of_people, actual_usage, month, year, predicted_usage
        FROM water_usage
        WHERE user_id = ?
        ORDER BY year DESC, month DESC
        LIMIT 1
    ''', (user_id,))
    result = cursor.fetchall()
    conn.close()

    if not result:
        return jsonify({"error": "No usage data found"}), 404
    
    price_per_liter = 3.00
    # ✅ Loop through `result` and create a list of dictionaries
    usage_data = [
        {
            "region": r[0],
            "number_of_people": r[1],
            "actual_usage": r[2],
            "month": r[3],
            "year": r[4],
            "predicted_usage": r[5],
            "estimated_bill": round(r[2] * price_per_liter, 2)
        } for r in result
    ]

    return render_template("dashboard.html", usage_data=usage_data)











if __name__ == "__main__":
    init_db()
    app.run(debug=True)


