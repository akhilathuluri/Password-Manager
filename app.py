from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///passwords.db'
db = SQLAlchemy(app)

# Password model
class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'appname': self.appname,
            'username': self.username,
            'password': self.password
        }

    def __repr__(self):
        return f"Password(appname={self.appname}, username={self.username})"

# Route to display the home template
@app.route('/')
@app.route('/home')
def home():
    passwords = Password.query.all()
    password_dicts = [password.to_dict() for password in passwords]
    return render_template('home.html', passwords=password_dicts)

# API endpoint to store passwords
@app.route('/passwords', methods=['POST'])
def store_password():
    appname = request.form.get('appname')
    username = request.form.get('username')
    password = request.form.get('password')
    
    new_password = Password(appname=appname, username=username, password=password)
    db.session.add(new_password)
    db.session.commit()
    
    return make_response(jsonify(message='Password stored successfully'), 200)

# API endpoint to search passwords by appname
@app.route('/passwords/search')
def search_passwords():
    search_query = request.args.get('appname')
    
    matched_passwords = Password.query.filter(Password.appname.ilike(f"%{search_query}%")).all()
    password_dicts = [password.to_dict() for password in matched_passwords]
    
    return make_response(jsonify(password_dicts), 200)

# Password authentication API endpoint
@app.route('/authenticate', methods=['POST'])
def authenticate_password():
    appname = request.form.get('appname')
    password = request.form.get('password')
    
    matched_password = Password.query.filter_by(appname=appname).first()
    
    if not matched_password:
        return make_response(jsonify(error='Password not found'), 404)
    
    if password != matched_password.password:
        return make_response(jsonify(error='Incorrect password'), 401)
    
    return make_response(jsonify(message='Authentication successful'), 200)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
