from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateTimeField


class AddTaskForm(FlaskForm):
    statement = TextAreaField('Условие', validators=[DataRequired()])
    correct_answer = StringField('Ответ', validators=[DataRequired()])
    points = IntegerField('Количество баллов')
    announce_time = DateTimeField('Время анонса', validators=[DataRequired()])
    start_time = DateTimeField('Время начала', validators=[DataRequired()])
    end_time = DateTimeField('Время окончания', validators=[DataRequired()])
    secret_key = IntegerField('Секретный ключ', validators=[DataRequired()])
    submit = SubmitField('OK')


class DeleteTaskForm(FlaskForm):
    id = IntegerField('ID задачи')
    secret_key = IntegerField('Секретный ключ', validators=[DataRequired()])
    submit = SubmitField('OK')
