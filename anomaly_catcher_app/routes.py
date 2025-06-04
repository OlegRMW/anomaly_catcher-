from anomaly_catcher_app import app
from anomaly_catcher_app import jsonify
from anomaly_catcher_app.forms import WheelMeasurementForm, FilterForm
from flask import render_template, flash, request, url_for, redirect
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import pandas as pd
from pathlib import Path
import math 

@app.route('/')
def greet_page():
    return render_template('greet_page.html')

@app.route('/home', methods=['GET', 'POST'])
def add_measurement():
    form = WheelMeasurementForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                if form.zamer_type.data == 'После обточки КП':
                    validation_error = validate_after_turning(form)
                    if validation_error:
                        flash(validation_error, 'danger')
                        return render_template('home_page.html', form=form)
                
                measurement_data = {
                    'user_change': form.user_change.data,
                    'date_change': form.date_change.data.strftime('%Y-%m-%d %H:%M:%S'),
                    'zamer_type': form.zamer_type.data,
                    'ep_num_wp': form.ep_num_wp.data,
                    'loco_11.tu17l1': float(form.tu17l1.data),
                    'loco_11.tu17r1': float(form.tu17r1.data),
                    'loco_11.tu17l2': float(form.tu17l2.data),
                    'loco_11.tu17r2': float(form.tu17r2.data),
                    'loco_11.tu17l3': float(form.tu17l3.data),
                    'loco_11.tu17r3': float(form.tu17r3.data),
                    'loco_11.tu17l4': float(form.tu17l4.data),
                    'loco_11.tu17r4': float(form.tu17r4.data),
                    'loco_11.tu17l5': float(form.tu17l5.data),
                    'loco_11.tu17r5': float(form.tu17r5.data),
                    'mean_prokat': (float(form.tu17l1.data) + float(form.tu17r1.data)) / 2,
                    'mean_diameter': (float(form.tu17l5.data) + float(form.tu17r5.data)) / 2,
                    'mean_tolshina_bandazha': (float(form.tu17l4.data) + float(form.tu17r4.data)) / 2,
                    'mean_tolshina_grebnya': (float(form.tu17l2.data) + float(form.tu17r2.data)) / 2,
                    'mean_crutizna_grebnya': (float(form.tu17l3.data) + float(form.tu17r3.data)) / 2
                }
                
                wear_level = classify_wear(measurement_data)
                measurement_data['wear_level'] = wear_level

                save_measurement(measurement_data) 
                
                flash('Данные успешно сохранены!', 'success')
                return redirect(url_for('add_measurement'))
                
            except Exception as e:
                flash(f'Произошла ошибка: {str(e)}', 'danger')
        
    return render_template('home_page.html', form=form)

#Проверка замеров после обточки
def validate_after_turning(form):
    
    csv_path = Path('anomaly_catcher_app/wheels.csv')
    
    if not csv_path.exists():
        return None  
    
    try:
        df = pd.read_csv(csv_path)
        prev_measurements = df[
            (df['ep_num_wp'] == form.ep_num_wp.data) & 
            (df['zamer_type'] == 'До обточки КП')
        ].sort_values('date_change', ascending=False)
        if len(prev_measurements) == 0:
            return None  
        
        last_before_turning = prev_measurements.iloc[0]
        
        MAX_ALLOWABLE_PROKAT = 0.5  
        TOLERANCE = 1.0 
        
        # 1. Проверка проката
        if form.tu17l1.data > MAX_ALLOWABLE_PROKAT:
            return 'Прокат левого бандажа после обточки превышает допустимое значение (0.5 мм)'
        
        if form.tu17r1.data > MAX_ALLOWABLE_PROKAT:
            return 'Прокат правого бандажа после обточки превышает допустимое значение (0.5 мм)'
        
        # 2. Проверка диаметра
        if form.tu17l5.data > last_before_turning['loco_11.tu17l5']:
            return 'Диаметр левого бандажа увеличился после обточки'
            
        if form.tu17r5.data > last_before_turning['loco_11.tu17r5']:
            return 'Диаметр правого бандажа увеличился после обточки'
        
        # 3. Проверка толщины бандажа
        if form.tu17l4.data > last_before_turning['loco_11.tu17l4']:
            return 'Толщина левого бандажа увеличилась после обточки'
            
        if form.tu17r4.data > last_before_turning['loco_11.tu17r4']:
            return 'Толщина правого бандажа увеличилась после обточки'
        
        # 4. Проверка соответствия изменений прокату
        expected_diameter_change = last_before_turning['loco_11.tu17l1']
        actual_diameter_change = last_before_turning['loco_11.tu17l5'] - form.tu17l5.data
        if abs(actual_diameter_change - expected_diameter_change) > TOLERANCE:
            return 'Некорректное изменение диаметра левого бандажа относительно проката'
        
        expected_diameter_change = last_before_turning['loco_11.tu17r1']
        actual_diameter_change = last_before_turning['loco_11.tu17r5'] - form.tu17r5.data
        if abs(actual_diameter_change - expected_diameter_change) > TOLERANCE:
            return 'Некорректное изменение диаметра правого бандажа относительно проката'
        
        # 5. Проверка толщины гребня (дополнительная)
        if 'loco_11.tu17l2' in last_before_turning:
            if abs(form.tu17l2.data - last_before_turning['loco_11.tu17l2']) > 0.5:
                return 'Толщина гребня левого бандажа изменилась более чем на 0.5 мм'
            
            if abs(form.tu17r2.data - last_before_turning['loco_11.tu17r2']) > 0.5:
                return 'Толщина гребня правого бандажа изменилась более чем на 0.5 мм'
        
        return None  
    
    except Exception as e:
        return f'Ошибка при проверке предыдущих замеров: {str(e)}'

#Классификация степени износа 
def classify_wear(data):
    """Классификация степени износа колесной пары"""
    levels = {
        'diameter': 'moderate',
        'bandazh': 'moderate',
        'grebny_weight': 'moderate',
        'grebny': 'moderate',
        'prokat': 'moderate'
    }
    #Проверки
    if data['mean_diameter'] < 950:  
        levels['diameter'] = 'critical'
    elif 950 <= data['mean_diameter'] < 1000:
        levels['diameter'] = 'moderate'
    elif 1000 <= data['mean_diameter'] <= 1250:
        levels['diameter'] = 'light'
    
    if data['mean_tolshina_bandazha'] < 50:  
        levels['bandazh'] = 'critical'
    elif 50 <= data['mean_tolshina_bandazha'] < 65:
        levels['bandazh'] = 'moderate'
    elif 65 <= data['mean_tolshina_bandazha'] <= 130:
        levels['bandazh'] = 'light'
    
    if data['mean_crutizna_grebnya'] > 9.5:  
        levels['grebny'] = 'critical'
    elif 8.5 < data['mean_crutizna_grebnya'] <= 9.5:
        levels['grebny'] = 'moderate'
    elif 6.5 <= data['mean_crutizna_grebnya'] <= 8.5:  
        levels['grebny'] = 'light'
    
    if 'mean_prokat' in data:
        if data['mean_prokat'] > 12: 
            levels['prokat'] = 'critical'
        elif 10 < data['mean_prokat'] <= 12:
            levels['prokat'] = 'moderate'
        elif 0 <= data['mean_prokat'] <= 10:
            levels['prokat'] = 'light'
    
    if data['mean_tolshina_grebnya'] < 26.0:
        levels['grebny_weight'] = 'critical'
    elif 26.0 <= data['mean_tolshina_grebnya'] < 28.0:
        levels['grebny_weight'] = 'moderate'
    elif 28.0 <= data['mean_tolshina_grebnya'] <= 33.0:
        levels['grebny_weight'] = 'light'
        
    if 'critical' in levels.values():
        return 'критический'
    elif 'moderate' in levels.values():
        return 'умеренный'
    elif 'light' in levels.values():
        return 'легкий'

def save_measurement(data):
    """Сохранение замера в CSV файл"""
    csv_path = Path('anomaly_catcher_app/wheels.csv')
    
    new_row = pd.DataFrame([data])
    
    if csv_path.exists():
        try:
            existing_data = pd.read_csv(csv_path)
            updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        except Exception as e:
            flash(f'Ошибка чтения файла: {str(e)}', 'danger')
            return redirect(url_for('add_measurement'))
    else:
        updated_data = new_row
    
    try:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        updated_data.to_csv(csv_path, index=False, encoding='utf-8')
    except Exception as e:
        flash(f'Ошибка сохранения: {str(e)}', 'danger')
        raise

@app.route('/wheels', methods=['GET', 'POST'])
def wheels_page():
    filter_form = FilterForm()
    csv_path = Path('anomaly_catcher_app/wheels.csv')
    df = pd.read_csv(csv_path)[['user_change','date_change','zamer_type','ep_num_wp', 'wear_level']]
    

    if request.args.get('ep_num_wp'):
        df = df[df['ep_num_wp'].astype(str) == str(request.args.get('ep_num_wp'))]
    
    if request.args.get('wear_category'):
        df = df[df['wear_level'] == request.args.get('wear_category')]
    
    page = request.args.get('page', 1, type=int)
    per_page = 9
    total_pages = math.ceil(len(df) / per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_df = df.iloc[start_idx:end_idx]
    
    filter_form.ep_num_wp.data = request.args.get('ep_num_wp', '')
    filter_form.wear_category.data = request.args.get('wear_category', '')
    
    return render_template(
        'wheels.html',
        df=paginated_df.to_dict(orient='index'),
        form=filter_form,
        current_page=page,
        total_pages=total_pages
    )
    
