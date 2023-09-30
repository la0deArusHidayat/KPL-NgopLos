from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
import jwt
import datetime
#import library untuk mebuat decorator
from functools import wraps

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'thisisthesecretkey'

# dekorator untuk kunci endpoint
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if token == None:
            return make_response(jsonify({'msg':'token missing'}), 200)
        try:
            output = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # return make_response(jsonify({'output':output}))
        except:
            return make_response(jsonify({'message':'Token is invalid'}), 403)

        return f(*args, **kwargs)
    return decorated

#1.Endpoint untuk login
class Login(Resource):
    def post(self):
        #butuh multipartform untuk transmisi data
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password == 'superadmin':
            token = jwt.encode(
                {'user':username,
                'exp':datetime.datetime.utcnow() + datetime.timedelta()
                }, 
                app.config['SECRET_KEY'], algorithm="HS256"
                )
            return jsonify({'token' : token})

        return jsonify({'msg':'Please Login to get access !'})

api.add_resource(Login, '/api/login', methods=['POST'])

if __name__ == "__main__":
    app.run(debug=True)
        
