import exc
import db
import send_link
from flask import render_template, request, abort, jsonify
from registration import RegistrationForm, send_registration_email
from . import app
from . import logger


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegistrationForm(request.form)

    if form.validate() and request.method == 'POST':
        reg = db.Register(form.email.data)
        is_success = reg.do_register()
        if is_success:
            send_registration_email(reg.email, reg.key)
            return render_template('register.html', title='Registered!',
                                   form=form, reg_results=is_success)
        elif not is_success:
            return render_template('register.html', title='Oops!',
                                   form=form, reg_results=is_success,
                                   error=reg.error)
    else:
        return render_template('register.html', title='Register',
                               form=form, show_registration=True)


@app.route('/verify/<veri_code>')
def verify(veri_code):
    verify = db.Verification(veri_code)
    result = verify.run_verification()
    if not result:
        return render_template('verify.html', title="Verify",
                               code=veri_code, result=verify.error)
    else:
        return render_template('verify.html', title="Verify",
                               code=veri_code, result=result)


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
        try:
            send_link.do_email(userid, request.json)
        except (exc.UserNotVerifiedException,
                exc.UserNotFoundException,
                exc.OverEmailSentLimitException,
                exc.JSONDoesntLookRightException) as e:
            logger.warning(e.message)
            return jsonify({'status': {'error': e.message}})
        else:
            return jsonify(status='OK')



