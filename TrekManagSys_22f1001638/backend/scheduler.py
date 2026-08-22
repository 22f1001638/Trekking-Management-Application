# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from application.jobs import send_daily_reminders, generate_monthly_report

# scheduler = BackgroundScheduler()


# def start_scheduler(app):
#     with app.app_context():
#         scheduler.add_job(
#             func=lambda: send_daily_reminders(app),
#             trigger=CronTrigger(hour=8, minute=0),
#             id='daily_reminders',
#             replace_existing=True,
#         )
#         scheduler.add_job(
#             func=lambda: generate_monthly_report(app),
#             trigger=CronTrigger(day=1, hour=8, minute=0),
#             id='monthly_report',
#             replace_existing=True,
#         )
#         scheduler.start()
#         app.logger.info('APScheduler started with daily and monthly jobs.')


# def shutdown_scheduler():
#     if scheduler.running:
#         scheduler.shutdown()
