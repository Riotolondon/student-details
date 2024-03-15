import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, LargeBinary
from sqlalchemy.sql import func
from enum import Enum

basedir = os.path.abspath(os.path.dirname(__file__))

# database connection
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class ApplicationStatus(Enum):
    SUCCESSFUL = "successful"
    REJECT = "reject"


# declaring the database table
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    surname = db.Column(db.String(150), nullable=False)
    id_number = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    course = db.Column(db.String(500), nullable=False)
    academic_background = db.Column(db.String(500), nullable=False)
    experience = db.Column(db.String(500), nullable=False)
    skills = db.Column(db.String(500), nullable=False)
    document = db.Column(LargeBinary)
    # document_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    status = Column(db.Enum(ApplicationStatus), nullable=True)

    def __repr__(self):
        return f'<Student {self.name}>'


# index routing
@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students, ApplicationStatus=ApplicationStatus)


# Create routing
@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        id_number = int(request.form['id_number'])
        email = request.form['email']
        course = request.form['course']
        academic_background = request.form['academic_background']
        experience = request.form['experience']
        skills = request.form['skills']
        status = ApplicationStatus[request.form['status'].upper()]


        if 'document' in request.files:
            document_file = request.files['document']
            if document_file.filename != '':
                document_content = document_file.read()
            else:
                document_content = None
        else:
            document_content = None

        student = Student(name=name,
                          surname=surname,
                          id_number=id_number,
                          email=email,
                          course=course,
                          academic_background=academic_background,
                          experience=experience,
                          skills=skills,
                          status=status,
                          document=document_content)

        db.session.add(student)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html', ApplicationStatus=ApplicationStatus)


# edit routing
@app.route('/<int:student_id>/edit/', methods=('GET', 'POST'))
def edit(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.status = ApplicationStatus[request.form['status'].upper()]
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', student=student, ApplicationStatus=ApplicationStatus)


# single display
# @app.route('/<int:student_id>/')
# def student(student_id):
#     student = Student.query.get_or_404(student_id)
#     return render_template('student.html', student=student, ApplicationStatus=ApplicationStatus)

@app.route('/student/<int:student_id>')
def student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student.html', student=student)


# delete routing
@app.route('/<int:student_id>/delete/', methods=['POST'])
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
