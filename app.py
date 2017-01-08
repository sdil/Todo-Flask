from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_humanize import Humanize
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField, BooleanField
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////flask/source/test.db'
app.config['SECRET_KEY'] = '123456' # enable csrf protection
db = SQLAlchemy(app)
humanize = Humanize(app)
RECAPTCHA_PUBLIC_KEY = '12345'
RECAPTCHA_PRIVATE_KEY = '123456'

# To setup DB and perform migrations only
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Set the ORM here
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    desc = db.Column(db.Text)
    category= db.Column(db.String(50))
    status = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.today().utcnow())

    def __init__(self, title, desc, category, status=False, date_created=datetime.today().utcnow()):
        self.title = title
        self.desc = desc
        self.category = category
        self.status = status
        self.date_created = date_created

    def __repr__(self):
        return '<title %r>' % self.title

class TodoForm(FlaskForm):
    CATEGORIES = [
        ('Personal', 'Personal'),
        ('Business', 'Business'),
        ("Others", "Others")
    ]

    title = StringField('Title')
    desc = StringField('Description', default="Testing")
    category = SelectField('Category', choices=CATEGORIES, default="Business")
    recaptcha = RecaptchaField()

class updateForm(TodoForm):
    status = BooleanField('Status')

# Set the routes
# index  DONE
# detail DONE
# create DONE
# update DONE
# delete DONE

@app.template_filter('is_Done')
def is_Done(status):
    if status == True:
        return "DONE"
    else:
        return "Not Done"

@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template('index.html', author="fadhil", todos=todos)

@app.route('/todo/<id>')
def detail(id):
    todo = Todo.query.filter_by(id=id).first_or_404()
    return render_template('detail.html', todo=todo)

@app.route('/todo/new', methods=['GET', 'POST'])
def new():
    form = TodoForm()
    if form.is_submitted():
        new_todo = Todo(form.title.data,
                        form.desc.data,
                        form.category.data)
        db.session.add(new_todo)
        db.session.commit()
        flash('Successfully added new todo task')
        return redirect(url_for('index'))
    return render_template('new.html', form=form)

@app.route('/todo/<id>/update', methods=['POST', 'GET'])
def update(id):
    todo = Todo.query.filter_by(id=id).first_or_404()
    form = updateForm(obj=todo)
    if form.is_submitted():
        todo.status = form.status.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', form=form)

@app.route('/todo/<id>/delete')
def delete(id):
    todo = Todo.query.filter_by(id=id).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/greet/<user>')
def greet(user):
    return render_template('greet.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
    manager.run()