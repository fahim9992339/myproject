# Step 1: Import necessary modules
from flask import *
import pymysql
import pymysql.cursors
import os
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

# Step 2: Initialize the app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/root/mysite/static/images'

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Step 3: Member Sign Up
@app.route("/api/signup", methods=['POST'])
def signup():
    NAME = request.form["NAME"]
    EMAIL = request.form['EMAIL']
    PHONE = request.form['PHONE']
    ADDRESS = request.form['ADDRESS']
    Customer = request.files['Customer_photo']

    filename = Customer.filename
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    Customer.save(photo_path)

    connection = pymysql.connect(host='localhost', user='root', password='', database='fashion and apparel')
    cursor = connection.cursor()

    sql = 'INSERT INTO customers (NAME, EMAIL, PHONE, ADDRESS, Customer_photo) VALUES (%s, %s, %s, %s, %s)'
    data = (NAME, EMAIL, PHONE, ADDRESS, filename)

    cursor.execute(sql, data)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Sign up successful"})

# Step 4: Member Sign In
@app.route('/api/signin', methods=["POST"])
def signin():
    NAME = request.form['NAME']
    PHONE = request.form['PHONE']

    connection = pymysql.connect(host='localhost', user='root', password='', database='fashion and apparel')
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM customers WHERE NAME=%s AND PHONE=%s"
    data = (NAME, PHONE)

    cursor.execute(sql, data)

    if cursor.rowcount == 0:
        message = {"message": "Login failed"}
    else:
        user = cursor.fetchone()
        message = {"message": "Login successful", "user": user}

    cursor.close()
    connection.close()

    return jsonify(message)

# Step 5: Add Fashion Product
@app.route("/api/add_fashion", methods=['POST'])
def add_fashion():
    Name = request.form["Name"]
    Brand = request.form["Brand"]
    Size = request.form["Size"]
    Color = request.form["Color"]
    Material = request.form["Material"]
    Gender = request.form["Gender"]
    Price = request.form["Price"]
    Stock_quantity = request.form["Stock_quantity"]
    Fashion_photo = request.files["Fashion_photo"]

    filename = Fashion_photo.filename
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    Fashion_photo.save(photo_path)

    connection = pymysql.connect(host='localhost', user='root', password='', database='fashion and apparel')
    cursor = connection.cursor()

    sql = "INSERT INTO fashion (Name, Brand, Size, Color, Material, Gender, Price, Stock_quantity, Fashion_photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    data = (Name, Brand, Size, Color, Material, Gender, Price, Stock_quantity, filename)

    cursor.execute(sql, data)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Product added successfully"})

# Step 6: Get All Fashion Products
@app.route("/api/get_fashion", methods=["GET"])
def products():
    connection = pymysql.connect(host="localhost", user="root", password="", database="fashion and apparel")
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM fashion"
    cursor.execute(sql)

    all_products = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(all_products)

# Step 7: Mpesa Payment Route
@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        amount = request.form['amount']
        phone = request.form['phone']

        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        data = response.json()
        access_token = "Bearer " + data['access_token']

        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"

        data_to_encode = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data_to_encode.encode())
        password = encoded.decode()

        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,  # now dynamic
            "PartyA": phone,
            "PartyB": business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://coding.co.ke/api/confirm.php",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers)

        print(response.text)

        return jsonify({"message": "An MPESA Prompt has been sent to your phone. Please check and complete payment"})

# Step 8: Run the application
if __name__ == "__main__":
    app.run(debug=True)
