from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:Ma19690022@acadmate-db.csmdb1acis22.us-east-2.rds.amazonaws.com:3306/acadmate'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)
db = SQLAlchemy(app)

handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

@app.before_request
def log_request_info():
    app.logger.warning('Request Headers: %s', request.headers)
    app.logger.warning('Request Body: %s', request.get_data())

@app.after_request
def log_response_info(response):
    app.logger.warning('Response Status Code: %s', response.status_code)
    app.logger.warning('Response Body: %s', response.get_data())
    return response 

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.VARCHAR(200), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    interest = db.Column(db.String(50))
    profile_pic = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('email', type=str)
parser.add_argument('interest', type=str)
parser.add_argument('id', type=str)
parser.add_argument('profile_pic', type=str)

class StudentResource(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if student:
            return {'id': student.id, 'name': student.name, 'email': student.email, 'interest': student.interest, 'profile_pic': student.profile_pic}
        else:
            return {'message': 'Student not found'}, 404
        
    def put(self, student_id):
        args = parser.parse_args()
        student = Student.query.get(student_id)

        if student:
            student.interest = args['interest']
            db.session.commit()
            return {'message': 'Student updated successfully'}
        else:
            return {'message': 'Student not found'}, 404
    
    def delete(self, student_id):
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return {'message': 'Student deleted successfully'}
        else:
            return {'message': 'Student not found'}, 404
        
class StudentsResource(Resource):
    def post(self):
        args = parser.parse_args()
        new_student = Student(id = args['id'], name=args['name'], email=args['email'], interest=args['interest'], profile_pic=args['profile_pic'])
        db.session.add(new_student)
        db.session.commit()
        return {'message': 'Student created successfully'}, 201


api.add_resource(StudentResource, '/students/<int:student_id>')
api.add_resource(StudentsResource, '/students/new')

if __name__ == '__main__':
    app.run()