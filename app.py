from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    priority = db.Column(db.String(10), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'
    
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        due_date_str = request.form.get('duedate')   # string from the form
        category = request.form.get('category')
        priority = request.form.get('priority')

        # Convert due_date string -> datetime (if provided)
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD."

        # Create new task with all fields
        new_task = Todo(
            content=task_content,
            due_date=due_date,
            category=category,
            priority=priority
        )

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"There was an issue adding your task: {e}"

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a error deleting this task'

from datetime import datetime

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        # Handle due date safely
        due_date_str = request.form.get('duedate')
        task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None

        # Category & priority
        task.category = request.form.get('category')
        task.priority = request.form.get('priority')

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'There was an error updating task: {e}'
        
    else:
        # Pre-fill form with existing task data
        return render_template('update.html', task=task)

if __name__ == "__main__":
    app.run(debug=True)