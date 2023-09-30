from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
api = Api(app)
CORS(app)

basedir = os.path.dirname(os.path.abspath(__file__))
database = "sqlite:///" + os.path.join(basedir, "db.sqlite")
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Memindahkan impor SQLAlchemy ke setelah pengaturan konfigurasi
db = SQLAlchemy(app)

class ModelDatabase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    umur = db.Column(db.Integer)
    alamat = db.Column(db.TEXT)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except:
            return False

identitas = {}

class AppResource(Resource):
    def get(self):
        #menampilkan data dari databse sqlite
        query = ModelDatabase.query.all()
        # melakukan iterasi pada model database
        output = [
            {
                "id":data.id,
                "nama":data.nama,
                "umur":data.umur,
                "alamat":data.alamat
            }
                for data in query
        ]
        response = {
            "code":200,
            "msg":"query data sukses",
            "data" : output
        }
        return response

    def post(self):
        data_nama = request.form.get("nama")
        data_umur = request.form.get("umur")
        data_alamat = request.form.get("alamat")

        model = ModelDatabase(nama=data_nama, umur=data_umur, alamat=data_alamat)
        model.save()

        response = {
            "msg": "Data berhasil dimasukkan",
            "code": 200
        }
        return response

    #delete all
    def delete(self):
        query = ModelDatabase.query.all()
        for data in query:
            db.session.delete(data) 
            db.session.commit()

        response = {
            "msg" : "semua data berhasil dihapus",
            "code" : 200
        }
        return response

#membuat Class bary untuk meng edit dan menghapus data\
class UpdateResource(Resource):
    def put(self, id):
        #konsumsi id itu untuk query di model databasenya
        #pilih data yang diedit berdasarkan id
        query = ModelDatabase.query.get(id)

        #form untuk edit data
        editNama = request.form["nama"]
        editUmur = request.form["umur"]
        editAlamat = request.form["alamat"]

        #mereplace nilai yang ada dis etipa field
        query.nama = editNama
        query.umur = editUmur
        query.alamat = editAlamat
        db.session.commit()

        response = {
            "msg": "edit data berhasil",
            "code" : 200
        }

        return response

    def delete(self, id):
        #konsumsi id itu untuk query di model databasenya
        #pilih data yang diedit berdasarkan id
        queryData = ModelDatabase.query.get(id)

        #panggil methode untuk delete data by id
        db.session.delete(queryData)
        db.session.commit()


        response = {
            "msg": "delete data berhasil",
            "code" : 200
        }

        return response

api.add_resource(AppResource, "/api", methods=["GET","POST","DELETE"])
api.add_resource(UpdateResource,"/api/<id>",methods=["PUT","DELETE"])


# Menambahkan konteks aplikasi sebelum memanggil db.create_all()
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
