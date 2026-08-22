import csv
import os
import threading
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from backend.model.TrekModel import BookingTable, Status, TrekTable, UserTable, Role
from backend.notifications import notify_user, notify_admin

EXPORT_STATUS = {}
EXPORT_FILES = {}


def _ensure_instance_dir():
    instance_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir, exist_ok=True)
    return instance_dir


def _send_daily_reminders():
    today = datetime.now()
    instance_dir = _ensure_instance_dir()
    output_file = os.path.join(instance_dir, 'daily_reminders.txt')
    treks = TrekTable.query.filter(TrekTable.start_date >= today.strftime('%Y-%m-%d')).order_by(TrekTable.start_date).all()
    reminders = []

    for trek in treks:
        if trek.status == Status.open:
            message = (
                f'Trek {trek.trek_name} starts on {trek.start_date}. '
                f'Location: {trek.location}. Available slots: {trek.available_slots}. '
                f'Prepare accordingly.'
            )
            reminders.append(message)
            bookings = BookingTable.query.filter_by(trek_id=trek.trek_id).all()
            for booking in bookings:
                user = UserTable.query.get(booking.user_id)
                if user and user.is_active:
                    notify_user(user, subject='Upcoming Trek Reminder', body=message)

    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        file.write('Daily Trek Reminders\n')
        file.write(f'Generated: {datetime.now()}\n\n')
        if reminders:
            file.write('\n'.join(reminders))
        else:
            file.write('No upcoming open treks found for reminders.')

    return output_file


def _generate_monthly_report():
    instance_dir = _ensure_instance_dir()
    output_file = os.path.join(instance_dir, 'monthly_trek_report.html')
    today = datetime.now()
    start_date = today.replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    treks = TrekTable.query.filter(TrekTable.start_date >= start_date.strftime('%Y-%m-%d')).filter(TrekTable.start_date <= end_date.strftime('%Y-%m-%d')).all()
    bookings = BookingTable.query.filter(BookingTable.booking_date >= start_date.strftime('%Y-%m-%d')).filter(BookingTable.booking_date <= end_date.strftime('%Y-%m-%d')).all()
    unique_users = {booking.user_id for booking in bookings}
    popular = {}
    for booking in bookings:
        popular[booking.trek_id] = popular.get(booking.trek_id, 0) + 1

    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        file.write('<html><head><meta charset="utf-8"><title>Monthly Trek Report</title></head><body>')
        file.write(f'<h1>Monthly Trek Activity Report - {today.year}-{today.month:02d}</h1>')
        file.write(f'<p>Total treks conducted this month: {len(treks)}</p>')
        file.write(f'<p>Total users participated: {len(unique_users)}</p>')
        file.write(f'<p>Total bookings this month: {len(bookings)}</p>')
        file.write('<h2>Popular Treks</h2>')
        file.write('<ul>')
        for trek_id, count in sorted(popular.items(), key=lambda x: x[1], reverse=True):
            trek = TrekTable.query.get(trek_id)
            if trek:
                file.write(f'<li>{trek.trek_name}: {count} bookings</li>')
        file.write('</ul>')
        file.write('</body></html>')

    try:
        with open(output_file, 'r', encoding='utf-8') as html_file:
            html_body = html_file.read()
    except Exception:
        html_body = None

    notify_admin(
        'Monthly Trek Activity Report',
        f'Monthly trek activity report is ready. View the report at {output_file}',
        html=html_body,
    )

    return output_file


def send_daily_reminders(app=None):
    if app:
        with app.app_context():
            return _send_daily_reminders()
    return _send_daily_reminders()


def generate_monthly_report(app=None):
    if app:
        with app.app_context():
            return _generate_monthly_report()
    return _generate_monthly_report()


def export_booking_history(user_id, app=None):
    EXPORT_STATUS[user_id] = 'queued'
    if app:
        thread = threading.Thread(target=_generate_export_csv, args=(user_id, app), daemon=True)
    else:
        thread = threading.Thread(target=_generate_export_csv, args=(user_id, current_app._get_current_object()), daemon=True)
    thread.start()
    return thread


def _generate_export_csv(user_id, app):
    with app.app_context():
        try:
            EXPORT_STATUS[user_id] = 'running'
            bookings = BookingTable.query.filter_by(user_id=user_id).all()
            instance_dir = _ensure_instance_dir()
            filename = f'booking_export_{user_id}.csv'
            output_file = os.path.join(instance_dir, filename)
            with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Booking ID', 'User ID', 'Trek Name', 'Location', 'Booking Date', 'Status', 'Payment Status'])
                for booking in bookings:
                    trek = TrekTable.query.get(booking.trek_id)
                    writer.writerow([
                        booking.booking_id,
                        booking.user_id,
                        trek.trek_name if trek else '',
                        trek.location if trek else '',
                        booking.booking_date,
                        booking.status.value if booking.status else '',
                        booking.payment_status,
                    ])
            EXPORT_FILES[user_id] = output_file
            EXPORT_STATUS[user_id] = 'completed'

            user = UserTable.query.get(user_id)
            if user:
                notify_user(
                    user,
                    subject='Your booking export is ready',
                    body=f'Your booking history export is complete. The file is available at {output_file}',
                )
        except (OSError, SQLAlchemyError) as ex:
            EXPORT_STATUS[user_id] = f'failed: {ex}'


def get_export_status(user_id):
    return EXPORT_STATUS.get(user_id, 'not_requested')


def get_export_file(user_id):
    return EXPORT_FILES.get(user_id)
