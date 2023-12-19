from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:Ma19690022@acadmate-db.csmdb1acis22.us-east-2.rds.amazonaws.com:3306/acadmate'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    interest = db.Column(db.String(50))

with app.app_context():
    db.create_all()

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name is required')
parser.add_argument('email', type=str, required=True, help='Email is required')
parser.add_argument('interest', type=str)

class StudentResource(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if student:
            return {'id': student.id, 'name': student.name, 'email': student.email, 'interest': student.interest}
        else:
            return {'message': 'Student not found'}, 404
        
    def put(self, student_id):
        args = parser.parse_args()
        student = Student.query.get(student_id)

        if student:
            student.name = args['name']
            student.email = args['email']
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
        new_student = Student(name=args['name'], email=args['email'], interest=args['interest'])
        db.session.add(new_student)
        db.sessoin.commit()
        return {'message': 'Student created successfully'}, 201


api.add_resource(StudentResource, '/students/<int:student_id>')
api.add_resource(StudentsResource, '/students/new')

if __name__ == '__main__':
    app.run()