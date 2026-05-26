import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Alarm
import pytz
import csv

def create_todoist_csv(json_file, csv_file, tz_str='America/Mexico_City'):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file}.")
        return

    tasks = []

    tz = pytz.timezone(tz_str)

    for taller in data.get('talleres', []) :
        event_name = taller.get('name')
        hours = taller.get('hours')
        days = taller.get('days')

        if not all([event_name, hours, days]):
            print(f"Skipping incomplete taller entry: {taller}")
            continue

        # Handle single or multiple hour ranges
        if not isinstance(hours, list):
            hours = [hours]

        for day_str in days:
            for hour_range in hours:
                try:
                    start_time_str, end_time_str = [x.strip() for x in hour_range.split('-')]
                    day = datetime.strptime(day_str, '%Y-%m-%d').date()

                    start_time = datetime.strptime(start_time_str, '%I:%M%p').time()
                    end_time = datetime.strptime(end_time_str, '%I:%M%p').time()

                    dt_start = tz.localize(datetime.combine(day, start_time))
                    dt_end = tz.localize(datetime.combine(day, end_time))

                    reminder_time = dt_start - timedelta(days=1)
                    reminder_time = reminder_time.replace(hour=20, minute=0, second=0)
                    tasks.append(['task', event_name, '', 4, 1, '', '', reminder_time.strftime('%Y-%m-%d %H:%M'), 'en', tz_str, '', '', '', ''])

                except (ValueError, IndexError) as e:
                    print(f"Skipping event due to parsing error: {taller} - {e}")
                    continue

    try:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['TYPE', 'CONTENT', 'DESCRIPTION', 'PRIORITY', 'INDENT', 'AUTHOR', 'RESPONSIBLE', 'DATE', 'DATE_LANG', 'TIMEZONE', 'DURATION', 'DURATION_UNIT', 'DEADLINE', 'DEADLINE_LANG'])
            writer.writerows(tasks)
        print(f"Successfully created {csv_file}")
    except IOError as e:
        print(f"Error writing to file {csv_file}: {e}")


if __name__ == '__main__':
    create_todoist_csv('talleres.json', 'tasks.csv')
