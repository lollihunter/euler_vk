from database import *
from flask import Flask, render_template, redirect
from add_task import *

app = Flask(__name__)

SECRET_KEY = 14882281337
app.config['SECRET_KEY'] = 'pivo_na_polu'


@app.route('/ok', methods=['GET', 'POST'])
def ok():
    return render_template('ok.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = AddTaskForm()
    form2 = DeleteTaskForm()
    if form.validate_on_submit():
        if form.secret_key.data == SECRET_KEY:
            new_task = Question(
                statement=form.statement.data,
                announce_time=form.announce_time.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                points=form.points.data,
                announced=0,
                correct_answer=form.correct_answer.data
            )
            session.add(new_task)
            session.commit()
            return redirect('/ok')
    if form2.validate_on_submit() and form.secret_key.data == SECRET_KEY:
        removed_task = session.query(Question).filter_by(id=form2.id.data).one_or_none()
        if removed_task is not None:
            session.delete(removed_task)
            session.commit()
            return redirect('/ok')
    return render_template('index.html', title='Добавить задачу', form=form, form2=form2)


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')