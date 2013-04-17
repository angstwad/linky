import exc
import db
import send_link
from flask import render_template, request, abort, jsonify, redirect, flash
from registration import RegistrationForm, send_registration_email
import recover
from . import app
from . import logger


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegistrationForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
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
                               form=form, show_form=True)


@app.route('/verify/<veri_code>')
def verify(veri_code):
    verify = db.Verification(veri_code)
    good_result = verify.run_verification()
    if not good_result:
        return render_template('verify.html', title="Verify",
                               code=veri_code, result=verify.error)
    else:
        return redirect('/user/%s' % veri_code)


@app.route('/recover', methods=['GET', 'POST'])
def recovery():
    form = recover.RecoverForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
        response = recover.do_recover(form.email.data)
        if isinstance(response['response'], str):
            flash(response['response'])
            return render_template('recover.html', title="Recover",
                                   form=form)
        else:
            redirect('/user/%s' % response['response']['key'])
    else:
            return render_template('recover.html', title="Recover",
                                   form=form, show_form=True)


@app.route('/user/<userid>')
def userpage(userid):
    return render_template('userpage.html', title='User Page',
                           userid=userid)
# TODO: Implement user's home page to get their bookmark

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



