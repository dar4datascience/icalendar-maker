import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Alarm
import pytz
import qrcode

def create_calendar_events(json_file, ics_file, tz_str='America/Mexico_City'):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file}.")
        return

    cal = Calendar()
    cal.add('prodid', '-//My Calendar//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', 'Cartelera Junio')

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

                    event = Event()
                    event.add('summary', event_name)
                    event.add('dtstart', dt_start)
                    event.add('dtend', dt_end)
                    event.add('dtstamp', datetime.now(pytz.utc))

                    # Add reminder
                    alarm = Alarm()
                    alarm.add('action', 'DISPLAY')
                    alarm.add('description', f'Reminder for {event_name}')
                    reminder_time = dt_start - timedelta(days=1)
                    reminder_time = reminder_time.replace(hour=20, minute=0, second=0)
                    alarm.add('trigger', reminder_time)
                    event.add_component(alarm)

                    cal.add_component(event)

                except (ValueError, IndexError) as e:
                    print(f"Skipping event due to parsing error: {taller} - {e}")
                    continue

    try:
        with open(ics_file, 'wb') as f:
            f.write(cal.to_ical())
        print(f"Successfully created {ics_file}")
    except IOError as e:
        print(f"Error writing to file {ics_file}: {e}")

def create_qr_code(url, file_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    print(f"Successfully created QR code at {file_path}")

if __name__ == '__main__':
    ICS_FILE = 'talleres.ics'
    QR_CODE_FILE = 'talleres_qr.png'
    # Replace this with the actual URL where you will host the .ics file
    URL_TO_ICS = 'YOUR_URL_HERE' 

    create_calendar_events('talleres.json', ICS_FILE)
    create_qr_code(f'webcal://{URL_TO_ICS}/{ICS_FILE}', QR_CODE_FILE)
