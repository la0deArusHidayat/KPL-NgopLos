# import library flask dan lainnya
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

# import library pendukung
import jwt
import os
import datetime

# inisialisasi objek flask dan lainnya
app = Flask(__name__)
api = Api(app)
CORS(app)

# konfigurasi database ==> create file db.sqlite
filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
db = SQLAlchemy(app)



# konfigurasi secret key
app.config['SECRET_KEY'] = "inirahasianegara"

# membuat schema model database authentikasi (login, register)
class AuthModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))

# membuat schema model Blog
class BlogModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(100))
    konten = db.Column(db.Text)
    penulis = db.Column(db.String(50))

# create model database ke dalam file db.sqlite


# membuat decorator
def butuh_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('datatoken')  # http://127.0.0.1:5000/api/blog?datatoken=fkjsldkjflskdjflskd
        if not token:
            return make_response(jsonify({"msg": "Token nggak ada bro!"}), 401)
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return make_response(jsonify({"msg": "Token nggak bener bro / invalid"}), 401)
        return f(*args, **kwargs)
    return decorator

# membuat routing endpoint
# routing authentikasi
class RegisterUser(Resource):
    # posting data dari front end untuk disimpan ke dalam database
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')

        # cek apakah username & password ada
        if dataUsername and dataPassword:
            # tulis data authentikasi ke db.sqlite
            dataModel = AuthModel(username=dataUsername, password=dataPassword)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"msg": "Registrasi berhasil"}), 200)
        return jsonify({"msg": "Username / password tidak boleh kosong"})


# routing untuk authentikasi: login
class LoginUser(Resource):
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')

        # query matching kecocokan data
        # iterasi authModel

        # cek username dan password
        queryUsername = [data.username for data in AuthModel.query.all()]
        queryPassword = [data.password for data in AuthModel.query.all()]
        if dataUsername in queryUsername and dataPassword in queryPassword:
            # klo login sukses
            # generate token authentikasi untuk user
            token = jwt.encode(
                {
                    "username": queryUsername, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                }, app.config['SECRET_KEY'], algorithm="HS256"
            )
            return make_response(jsonify({"msg": "Login Sukses", "token": token}), 200)

        # klo login gagal
        return jsonify({"msg": "Login gagal, silahkan coba lagi !!!"})

# inisiasi resource api
api.add_resource(RegisterUser, "/api/register", methods=["POST"])
api.add_resource(LoginUser, "/api/login", methods=["POST"])

# Menambahkan konteks aplikasi sebelum memanggil db.create_all()
with app.app_context():
    db.create_all()

# jalankan aplikasi app.py
if __name__ == "__main__":
    app.run(debug=True)
