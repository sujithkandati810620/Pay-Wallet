from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
import bcrypt
import random
import urllib.parse

app = Flask(__name__)
app.secret_key = "testing"
username = urllib.parse.quote_plus('Applicationuser')
password = urllib.parse.quote_plus('Vishnu@abcd')

client = MongoClient("mongodb+srv://%s:%s@cluster0.qxxslmd.mongodb.net/?retryWrites=true&w=majority" %(username, password))
db = client.get_database('appdata')
users = db.register
money= db.balance
otp=random.randint(1000,9999)
otp_check = False
otp_money = 0
email_pass_change = ""

@app.route("/")
def enter():
    return render_template('login.html')

@app.route("/mobile.html")
def mobile():
    return render_template('mobile.html')

@app.route("/electricbill.html")
def electricbilll():
    return render_template('electricbill.html')

@app.route("/successful.html")
def SUCCESS():
    return render_template('successful.html')

@app.route("/mobile_recharge.html")
def recharge():
    return render_template('mobile_recharge.html')

@app.route("/wallet")
def wallet():
    return render_template('wallet.html')

@app.route("/register.html")
def pageenter():
    return render_template('register.html')
@app.route("/email.html")
def pagenter():
    return render_template('email.html')
@app.route("/profile.html")
def profile():
    return render_template('profile.html')
@app.route("/passwordchange.html")
def passwordchange():
    return render_template('passwordchange.html')

@app.route("/register", methods=['POST', 'GET'])
def index():
    message = ''
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        DOB = request.form.get("DOB")
        gender = request.form.get("gender")
        mobile = request.form.get("mobile")
        address = request.form.get("address")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        
        email_found = users.find_one({"email": email})
        if len(mobile) !=10:
            message = 'enter a valid number'
            return render_template('register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('register.html', message=message)
        if len(password1) <6:
            message = 'enter another password'
            return render_template('register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'firstname': firstname,'lastname': lastname,'DOB': DOB,'gender': gender,'mobile': mobile,'address': address,'email': email, 'password': hashed}
            users.insert_one(user_input)
            
           
            user_data = users.find_one({"email": email})

            new_email = user_data['email']

            add_fields = {"email":email,"balance":0,"cards":[]}

            money.insert_one(add_fields)
   
            return render_template('login.html', email=new_email)
    return render_template('login.html')

@app.route('/logged_in')
def logged_in():
        return render_template('index.html')


@app.route("/login", methods=[ "GET"])
def login():
    return render_template('login.html')


@app.route("/passchange",methods=["POST"])
def pchange():
    p1 = request.form.get("p1")
    p2 = request.form.get("p2")
    global email_pass_change
    if p1!=p2:
        return "enter valid passwords"
    hashed = bcrypt.hashpw(p2.encode('utf-8'), bcrypt.gensalt())
    doc = users.find_one_and_update(
    {"email" : email_pass_change},
    {"$set":
    {"password" : hashed}})
    return render_template("login.html") 

# @app.route("/password",methods=["POST"])
# def passwoed():
#     global email_pass_change
#     email = request.form["email"]
#     email_found = users.find_one({"email": email})
#     if email_found:
#         email_pass_change = email
#         email_alert("hey", "hello"+str(otp), [email])
#         return render_template("otp.html")
    # else:
    #     return "enter valid email"
# @app.route('/validate',methods=["POST"])   
# def validate():  
#     user_otp = request.form['otp']  
#     if otp == int(user_otp):  
#         return render_template("passwordchange.html")
#     else:
#         return "<h3>failure, OTP does not match</h3>"

@app.route('/addcard', methods=["Post"])   
def addcards():  
   print(request.form)
   money.update_one(
        {'email': session['email']},
        {'$push': {'cards': request.form}}
    )
   return render_template("wallet.html")

@app.route('/card.html')   
def acard():  
    return render_template("card.html")

@app.route('/savedcards.html')   
def savedcards():  
    doc = money.find_one({"email":session['email']})
    return render_template("savedcards.html", data= doc['cards'])

@app.route('/verifycvv', methods=["POST"])   
def cvv():
    doc = money.find_one({"email":session['email']}) 
    for i in doc['cards']:
        if(i['number']==request.form['card'] and i['cvv']==request.form['cvv']):
            balance =  money.find_one({"email":session['email']})['balance']
            finalmoney = balance+int(request.form['money'])
            money.update_one({'email': session['email']}, {'$set': {'balance': finalmoney}})
            return render_template('savedcards.html', message = "Successful")
        else:
            doc = money.find_one({"email":session['email']})
            return render_template('savedcards.html', data= doc['cards'], message = "Enter valid cvv")

# @app.route('/validate1',methods=["POST"])   
# def validate1():  
#     user_otp = request.form['otp']  
#     global otp_check
#     if otp == int(user_otp):
#         otp_check = True
#         return redirect(url_for('addmoney'))
#     else:
#         return "<h3>failure, OTP does not match</h3>"

@app.route("/login", methods=["POST"])
def loging():
    email = request.form.get("email")
    password = request.form.get("password")
    email_found = users.find_one({"email": email})
    
    if email_found:
        email_val = email_found['email']
        passwordcheck = email_found['password']

        if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
            session["email"] = email_val

            return redirect(url_for('logged_in'))
        else:
            message = 'invalid credentials'
            return render_template('login.html', message=message)
    else:
        message = 'Email not found'
        return render_template('login.html', message=message)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("login.html")
    else:
        return render_template('login.html')

@app.route("/balance",methods=["GET"])
def balance():
  if 'email' not in session:
        return render_template("login.html")
  doc = money.find_one(
    {"email" : session['email']})
  return render_template('balance.html', data = doc)

@app.route("/reducebalance",methods=["POST"])
def reduce_balance():
    if 'email' not in session:
        return render_template("login.html")
    else:
        balance =  money.find_one({"email":session['email']})['balance']
        final_money = balance-int(request.form['amount'])
        if final_money < 0 :
            return render_template('wallet.html', message = "Amount not sufficient!! Add more amount!!")
        money.update_one({'email': session['email']}, {'$set': {'balance': final_money}})
        return render_template('wallet.html', message = "Successful")

@app.route("/profileshow",methods=["GET"])
def show():
  if 'email' not in session:
        return render_template("login.html")
  doc = users.find_one(
    {"email" : session['email']},
  )
  return render_template('profile.html', data=doc)

# @app.route("/addmoney")
# def addmoney():
#     global otp_check
#     global otp_money
#     if otp_check == True:
#         balance =  money.find_one({"email":session['email']})['balance']
#         finalmoney = balance+otp_money
#         money.update_one({'email': session['email']}, {'$set': {'balance': finalmoney}})
#         otp_check = False
#         otp_money = 0
#         return render_template("wallet.html")    
#     return ("invalid")

@app.route("/profilechange",methods=["post"])
def change():
  doc = users.find_one_and_update(
    {"email" : session['email']},
    {"$set":
        {"firstname" : request.form.get("firstname"),
        "lastname" : request.form.get("lastname"),
        "DOB" : request.form.get("DOB"),
        "gender" : request.form.get("gender"),
        "mobile" : request.form.get("mobile"),
        "address" : request.form.get("address")
        }
    }
  )
  return render_template('index.html')
if __name__ == "__main__":
  app.run(debug=True)

