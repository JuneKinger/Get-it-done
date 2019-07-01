from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:june@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    # Sometimes we may actually want to remove/delete a row
    # from the db, but often a functionality would be to keep
    # deleted tasks and just have a boolean flag that told us
    # whether or not they were deleted and then have our appln
    # sift through them and only display non-complete tasks or
    # complete tasks depending on the situation. To do that, we 
    # add a new property to our task class with a boolean
    # to indicate whether a given task has been completed.
    # Either place a default value like below or with self. below
    # completed = db.Column(db.Boolean, default=False)
    
    completed = db.Column(db.Boolean)
    def __init__(self, name):
        self.name = name
        self.completed = False
    # we would need to recreate the table to include the new
    # completed column as we did before at the shell
    # >>> from main import db, Task
    # >>> db.create_all() - looks for classes that have not
    # been created yet and it creates them. In this case, 
    # our task table already existed so db.create_all()
    # did not update or re-create the table - it just left it
    # as it is.
    # In order for the new column to be pushed through, I need to
    # destroy the task table and then recreate it. So we lose
    # any data that is part of that. For this, we use:
    # >>> db.drop_all()
    # >>> db.create_all() - now recreates the table with column completed.
    # flask-migrate will keep your data intact and not destroy it

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        # create new task object from constructor Task
        new_task = Task(task_name)
        # place in database and then commit to push it in.
        db.session.add(new_task)
        db.session.commit()


    # render template to pass ALL of the tasks objects out from the database.
    # first request the server for all of the task objects
    # tasks = Task.query.all()
    # we can filter for only certain tasks with a filter by
    # and get only those from the db to display in the main view
    tasks = Task.query.filter_by(completed=False).all()
    # also display completed tasks 
    completed_tasks = Task.query.filter_by(completed=True).all()
    return render_template('todos.html',title="Get It Done!", 
    tasks=tasks, completed_tasks=completed_tasks)

@app.route('/delete-task', methods=['POST'])

# handler delete_task
def delete_task():
    # convert the data to int since id is int type
    task_id = int(request.form['task-id'])
    # to delete this task with the task_id, I need to get
    # the specific task object from the database with the specific id 
    # and send the request to the server with the object we are passing in, that is, task_id
    task = Task.query.get(task_id)
    # if we just want to flag our field for delete instead of
    # actually deleting it
    task.completed = True
    db.session.add(task)
    db.session.commit()

    # if we want to actually delete the row, we first flag 
    # the object for deletion
    # db.session.delete(task)
    # actually delete the database row for that id
    # db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run()