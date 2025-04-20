from flask import Flask, render_template, request, redirect, flash
import pymysql
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Used for flashing messages

# Connect to DB
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='Ansh133@',
        db='blooddonation',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT 
                bs.blood_type,
                bb.blood_bank_name,
                bb.baddress,
                bs.units_available
            FROM blood_stock bs
            JOIN blood_bank bb ON bs.blood_bank_id = bb.blood_bank_id
            ORDER BY bb.blood_bank_name, bs.blood_type
        """)
        blood_data = cursor.fetchall()
    conn.close()
    return render_template('home.html', blood_data=blood_data)

@app.route('/donate_blood', methods=['GET', 'POST'])
def donate_blood():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            name = request.form['name']
            phone = request.form['phone']
            blood_type = request.form['blood_type']
            units = request.form['units']
            blood_bank_id = request.form['blood_bank']

            # Optional fields, we set defaults if they are empty or None
            dob = request.form.get('dob')
            gender = request.form.get('gender')
            address = request.form.get('address')

            # Use safe default values if the fields are not provided
            weight = request.form.get('weight', None)
            bp = request.form.get('bp', None)
            iron = request.form.get('iron', None)
            doctor_id = request.form.get('doctor_id', None)

            # Convert to integer only if they have values (avoid 'NoneType' error)
            if weight:
                weight = int(weight)
            if bp:
                bp = int(bp)
            if iron:
                iron = int(iron)
            if units:
                units = int(units)
            if doctor_id:
                doctor_id = int(doctor_id)

            cursor.execute("""
                INSERT INTO donor 
                (donor_name, phone_no, DOB, gender, address, weight, blood_pressure, iron_content, doctor_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, phone, dob, gender, address, weight, bp, iron, doctor_id))

            cursor.execute("""
                SELECT * FROM blood_stock 
                WHERE blood_type = %s AND blood_bank_id = %s
            """, (blood_type, blood_bank_id))
            stock = cursor.fetchone()

            if stock:
                cursor.execute("""
                    UPDATE blood_stock 
                    SET units_available = units_available + %s 
                    WHERE blood_type = %s AND blood_bank_id = %s
                """, (units, blood_type, blood_bank_id))
            else:
                cursor.execute("""
                    INSERT INTO blood_stock (blood_type, blood_bank_id, units_available)
                    VALUES (%s, %s, %s)
                """, (blood_type, blood_bank_id, units))

            conn.commit()
            flash("✅ Blood donation recorded successfully!", "success")
            return redirect('/')

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error: {e}", "error")
            return redirect('/donate_blood')
        finally:
            conn.close()

    cursor.execute("SELECT * FROM blood_bank")
    blood_banks = cursor.fetchall()
    conn.close()
    return render_template('donate_blood.html', blood_banks=blood_banks)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        if not name or not username or not phone or not email or not password:
            flash("❌ All fields are required.", "error")
            return redirect('/register')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, username, phone, email, password) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, username, phone, email, password))
                conn.commit()
                flash("✅ Registered successfully", "success")
                return redirect('/')
        except Exception as e:
            conn.rollback()
            flash(f"❌ Registration failed: {e}", "error")
            return redirect('/register')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/request_blood', methods=['GET', 'POST'])
def request_blood():
    if request.method == 'POST':
        phone = request.form['phone']
        blood_type = request.form['blood_type']
        units_requested = int(request.form['units'])

        if not phone or not blood_type or not units_requested:
            flash("❌ All fields are required.", "error")
            return redirect('/request_blood')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
                user = cursor.fetchone()
                if not user:
                    flash("❌ User not found. Please register first.", "error")
                    return redirect('/register')

                cursor.execute("""
                    SELECT blood_type, blood_bank_id, units_available
                    FROM blood_stock
                    WHERE blood_type = %s AND units_available >= %s
                    ORDER BY units_available DESC
                    LIMIT 1
                """, (blood_type, units_requested))
                stock = cursor.fetchone()

                if not stock:
                    flash("❌ Not enough stock available.", "error")
                    return redirect('/request_blood')

                cursor.execute("""
                    INSERT INTO blood_request (user_id, blood_type, units_requested, request_date, status)
                    VALUES (%s, %s, %s, %s, 'Pending')
                """, (user['id'], blood_type, units_requested, date.today()))

                cursor.execute("""
                    UPDATE blood_stock 
                    SET units_available = units_available - %s
                    WHERE blood_type = %s AND blood_bank_id = %s
                """, (units_requested, stock['blood_type'], stock['blood_bank_id']))

                conn.commit()
                flash("✅ Blood request submitted successfully!", "success")
                return redirect('/')

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error: {e}", "error")
            return redirect('/request_blood')
        finally:
            conn.close()

    return render_template('request_blood.html')

@app.route('/donor_list')
def donor_list():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT donor_name, phone_no FROM donor")
            donors = cursor.fetchall()  # Fetch minimal donor info
    finally:
        conn.close()

    return render_template('donor_list.html', donors=donors)

@app.route('/view_requests', methods=['GET', 'POST'])
def view_requests():
    if request.method == 'POST':
        phone = request.form.get('phone')

        if not phone:
            flash("❌ Phone number is required.", "error")
            return redirect('/view_requests')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
                user = cursor.fetchone()

                if not user:
                    flash("❌ No user found with this phone number.", "error")
                    return redirect('/view_requests')

                cursor.execute("SELECT * FROM blood_request WHERE user_id = %s", (user['id'],))
                requests = cursor.fetchall()

                if not requests:
                    flash("❌ No requests found.", "error")
                    return render_template("view_requests.html", requests=[])

                return render_template("view_requests.html", requests=requests)

        finally:
            conn.close()

    return render_template("view_requests_form.html")

if __name__ == '__main__':
    app.run(debug=True)
