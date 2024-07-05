from flask import Flask, render_template, request
import datetime
import random
import os

app = Flask(__name__)

def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()

@app.route('/')
def home():
    return render_template('index.html')

def read_session_content(session_type):
    session_type = session_type.lower()  # Convert to lowercase
    if session_type == 'endurance':
        session_dir = os.path.join('endurance')
    elif session_type == 'strength/endurance':
        session_dir = os.path.join('strendurance')
    elif session_type == 'strength':
        session_dir = os.path.join('strength')
    else:
        return 'No additional content available for this session type.'

    if os.path.exists(session_dir):
        filenames = os.listdir(session_dir)
        if filenames:
            filename = random.choice(filenames)
            filepath = os.path.join(session_dir, filename)
            return read_file(filepath)
    
    return 'No additional content available for this session type.'

@app.route('/create_plan', methods=['POST'])
def create_plan():
    training_type = request.form['training_type']
    weeks = int(request.form['weeks'])
    days_per_week = int(request.form['days_per_week'])
    hours_per_day = float(request.form['hours_per_day'])
    start_date = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d')

    warmup = read_file(os.path.join('static', 'warmup.txt'))
    cooldown = read_file(os.path.join('static', 'cooldown.txt'))

    if training_type == 'base':
        percentages = {'endurance': 70, 'strength/endurance': 20, 'strength': 10}
    else:
        percentages = {'endurance': 20, 'strength/endurance': 60, 'strength': 20}

    total_sessions = weeks * days_per_week
    endurance_sessions = int(total_sessions * percentages['endurance'] / 100)
    strength_endurance_sessions = int(total_sessions * percentages['strength/endurance'] / 100)
    strength_sessions = total_sessions - endurance_sessions - strength_endurance_sessions

    sessions = (['endurance'] * endurance_sessions +
                ['strength/endurance'] * strength_endurance_sessions +
                ['strength'] * strength_sessions)
    random.shuffle(sessions)

    plan = []
    current_date = start_date
    rest_days_needed = 0

    for week in range(weeks):
        week_plan = []
        for day in range(days_per_week):
            if rest_days_needed > 0:
                week_plan.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'session': 'Rest Day',
                    'warmup': '',
                    'main_session': '',
                    'cooldown': ''
                })
                rest_days_needed -= 1
                current_date += datetime.timedelta(days=1)
                continue

            if sessions:
                session = sessions.pop(0)
                main_session = read_session_content(session)
                week_plan.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'session': session,
                    'warmup': warmup,
                    'main_session': main_session,
                    'cooldown': cooldown
                    
                })
                current_date += datetime.timedelta(days=1)

                if session == 'strength/endurance':
                    rest_days_needed = max(rest_days_needed, 1)
                elif session == 'strength':
                    rest_days_needed = max(rest_days_needed, 2)

        while current_date.weekday() != 0 and (sessions or rest_days_needed > 0):  # Move to the next Monday if there are sessions left
            current_date += datetime.timedelta(days=1)

        plan.append(week_plan)

    return render_template('plan.html', plan=plan, weeks=weeks)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False,port=5001)