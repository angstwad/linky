from . import app
from . import logger
from flask import render_template, request, abort, jsonify
from registration import registration_form, send_registration_email
from send import send_link_email
import exc
import db

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = registration_form(request.form)

    if form.validate() and request.method == 'POST':
        db_result = db.register(form.email.data).do_register()

        if isinstance(db_result, tuple):
            if db_result.is_good is True:
                send_registration_email(db_result.email, db_result.hash)
                return render_template('register.html', title='Registered!', form=form, db_results=db_result)
            elif db_result.is_good is False:
                return render_template('register.html', title='Oops!', form=form, db_results=db_result)
        else:
            abort(500)
    else:
        return render_template('register.html', title='Register', form=form, do_register=True)


@app.route('/verify/<veri_code>')
def verify(veri_code):
    result = db.verification(veri_code).run_verification()
    return render_template('verify.html', title="Verify", code=veri_code, result=result)


@app.route('/recover')
def recover():
    return render_template('recover.html')


@app.route('/user/<userid>/send', methods=['POST'])
def send(userid):
    if not isinstance(userid, unicode):
        print "isinstance"
        abort(401)
    elif not userid.isalnum():
        print "isalnum"
        abort(401)
    elif not len(userid) == 40:
        print "userid.len"
        abort(400)
    elif not request.json:
        abort(400)
    else:
        status = None
        try:
            send_link_email(userid, request.json)
        except (exc.UserNotVerifiedException, exc.UserNotFoundException, exc.OverEmailSentLimitException,
                exc.JSONDoesntLookRightException) as e:
            logger.exception(e.message)
            status = e.message
        else:
            status = 'OK'
        finally:
            return jsonify(status=status)
