import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../..')
from jenkins_app.base import JenkinsBase
from helpers.datetime_helper import timestamp_to_datetime, current_datetime
from message_app import AlertMail


import click
@click.command()
@click.option('--job_path')
@click.option('--mail_to')
@click.option('--minutes_range')
def run(job_path, mail_to, minutes_range):
    def get_record(job_path):
        jenkins = JenkinsBase()
        response = jenkins.get_last_build(job_path)
        return {
            'result': response['result'],
            'datetime': timestamp_to_datetime(response['timestamp']/1000),
            'client': job_path.split('/job/')[1],
            'job': job_path.replace('/job/', '/')
        }

    def sent_alert_mail(record, x_minutes_ago):
        record['datetime'] = str(record['datetime'])
        body = f'''
            Job stagnant alert!!
            Last built job: {record}.
            How many minutes ago job excuted: {x_minutes_ago}.
        '''
        print(f'Sent mail body: {body}')
        mail = AlertMail().send(body, mail_to)
        print(f'Mail sent: {mail}')

    record = get_record(job_path)

    x_minutes_ago = (current_datetime() - record['datetime']).total_seconds() / 60
    is_stopped = x_minutes_ago > int(minutes_range)
    print(f'True & alert if the job is stopped: {is_stopped}')

    if is_stopped:
        sent_alert_mail(record, x_minutes_ago)

    # print(f'Insert record: {record}')


if __name__ == '__main__':
    run()
# python detect_stagnant.py --job_path '/job/kamika_aster_one/job/remind_mail' --mail_to 'emata@espalhar.net' --minutes_range 30
