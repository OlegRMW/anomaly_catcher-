from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange, InputRequired, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd

class WheelMeasurementForm(FlaskForm):
    
    user_change = StringField('Оператор', validators=[DataRequired(message="Укажите оператора")])
    date_change = DateField('Дата замера', default=datetime.now, validators=[])
    zamer_type = SelectField(
        label='Выберите тип замера',
        choices=[
            ('', 'Выберите тип замера'), 
            ('Контрольный замер КП', 'Контрольный замер КП'), 
            ('До ремонта КП', 'До ремонта КП'), 
            ('До обточки КП', 'До обточки КП'), 
            ('После обточки КП', 'После обточки КП'),
            ('До смены (перекатки)  КП', 'До смены (перекатки)  КП'),
            ('После смены (перекатки)  КП', 'После смены (перекатки)  КП'),
            ('После ремонта КП', 'После ремонта КП'),
            ('планового инспекционного контроля ЦТА ОАО "РЖД"', 'планового инспекционного контроля ЦТА ОАО "РЖД"')
        ],
        validators=[DataRequired(message="Пожалуйста, выберите тип замера")]
    )
    ep_num_wp = IntegerField('Номер колесной пары', validators=[DataRequired(message="Укажите номер колесной пары")])

    tu17l1 = FloatField('Прокат L1 (мм)', validators=[
        NumberRange(min=0, max=15, message="Допустимый диапазон 0-15 мм"),
        InputRequired(message="Укажите значение проката")
    ])
    tu17r1 = FloatField('Прокат R1 (мм)', validators=[
        NumberRange(min=0, max=15, message="Допустимый диапазон 0-15 мм"),
        InputRequired(message="Укажите значение проката")
    ])
    
    tu17l2 = FloatField('Толщина гребня L2 (мм)', validators=[
        NumberRange(min=10, max=33, message="Допустимый диапазон 10-33 мм"),
        DataRequired(message="Укажите толщину гребня")
    ])
    tu17r2 = FloatField('Толщина гребня R2 (мм)', validators=[
        NumberRange(min=10, max=33, message="Допустимый диапазон 10-33 мм"),
        DataRequired(message="Укажите толщину гребня")
    ])
    
    tu17l3 = FloatField('Крутизна гребня L3 (мм)', validators=[
        NumberRange(min=5, max=12, message="Допустимый диапазон 5-12 мм"),
        DataRequired(message="Укажите крутизну гребня")
    ])
    tu17r3 = FloatField('Крутизна гребня R3 (мм)', validators=[
        NumberRange(min=5, max=12, message="Допустимый диапазон 5-12 мм"),
        DataRequired(message="Укажите крутизну гребня")
    ])
    
    tu17l4 = FloatField('Толщина бандажа L4 (мм)', validators=[
        NumberRange(min=10, max=130, message="Допустимый диапазон 10-130 мм"),
        DataRequired(message="Укажите толщину бандажа")
    ])
    tu17r4 = FloatField('Толщина бандажа L4 (мм)', validators=[
        NumberRange(min=10, max=130, message="Допустимый диапазон 10-130 мм"),
        DataRequired(message="Укажите толщину бандажа")
    ])
    
    tu17l5 = FloatField('Диаметр L5 (мм)', validators=[
        NumberRange(min=900, max=1250, message="Допустимый диапазон 900-1250 мм"),
        DataRequired(message="Укажите диаметр бандажа")
    ])
    tu17r5 = FloatField('Диаметр R5 (мм)', validators=[
        NumberRange(min=900, max=1250, message="Допустимый диапазон 900-1250 мм"),
        DataRequired(message="Укажите диаметр бандажа")
    ])
    

    submit = SubmitField(label = 'Сохранить') 

class FilterForm(FlaskForm):
    ep_num_wp = IntegerField('Номер колесной пары', validators=[Optional()])
    wear_category = SelectField(
        choices=[
            ('', 'Выберите категорию износа'), 
            ('', 'Нет'), 
            ('легкий', 'легкий'), 
            ('умеренный', 'умеренный'), 
            ('критический', 'критический')
        ]
    )
    submit = SubmitField(label = 'Применить фильтр')