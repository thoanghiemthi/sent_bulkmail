from flask import Flask, request,flash, render_template,session,redirect,url_for
from flask_mail import Mail, Message
import os
import time
import random
import datetime
from celery import Celery
app = Flask(__name__)
app.config['SECRET_KEY']= 'top'
# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'hongnguye617@gmail.com'

# use the app password created
app.config['MAIL_PASSWORD'] = 'ncwgybvfuejatcni'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = "hongnguyen617@gmail.com"
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'
mail = Mail(app)
celery = Celery(app.name,broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
@celery.task
def send_async_email(email_data):
    # with mail.connect() as conn:
    #     users =email_data['to'].split(',')
    #     for user in users:
    #         # time_n = datetime.datetime()
    #
    #         message = 'Hello '
    #         subject = email_data['subject']
    #         msg = Message(recipients=[user],
    #                       body=message,
    #                       subject=subject)
    #         conn.send(msg)

    msg = Message(email_data['subject'],sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    with app.app_context():
        mail.send(msg)

@app.route('/send/<listmail>')
def sendmail(listmail):
    listmail = listmail.split(',')
    print("listmail",listmail)
    body = "Detected change in reloading"
    for umail in listmail:
        email_datass = {"subject":"hello ", "to" : umail, 'body': body}
        send_async_email.delay(email_datass)
    return "done"

@app.route("/", methods=['GET', 'POST'])
def index():
    try:
        # if it is a post request
        if request.method == 'GET':
            return render_template('index.html', email = session.get('email',''))
        email = request.form['email']
        session['email'] = email
        if request.form['submit'] == 'Send':

            users = email.split(',')
            body = 'If, for some reason, the client is configured to use a different backend than the worker, you won’t be able to receive the result. Make sure the backend is configured correctly:'
            for user in users:
                email_data = {"subject":"hello ", "to" : user, 'body': body}
                print("email_data",email_data)
                send_async_email.delay(email_data)
            flash('Sending email to {0}'.format(email))
        return redirect(url_for('index'))
    except Exception as e:
        return f'<p>{e} </p>'

if __name__ == '__main__':
    app.run(debug=True)