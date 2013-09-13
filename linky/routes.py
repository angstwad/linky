from flask import render_template, request, abort, jsonify, redirect, flash
import exc
import db
import send_link
import registration
import recover
from . import app
from . import logger


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def registry():
    form = registration.RegistrationForm(request.form)
    if form.validate():
        reg = db.Register(form.email.data)
        is_success = reg.do_register()
        if is_success:
            registration.send_registration_email(reg.email, reg.key)
            return render_template('register.html', title='Registered!',
                                   register_active='active', form=form,
                                   reg_results=is_success)
        elif not is_success:
            return render_template('register.html', title='Oops!',
                                   register_active='active', form=form,
                                   reg_results=is_success, error=reg.error)
    else:
        return render_template('register.html', title='Register',
                               register_active='active', form=form,
                               show_form=True)


@app.route('/verify/<veri_code>/')
def verify(veri_code):
    v = db.Verification(veri_code)
    v_result = v.run_verification()
    if not v_result:
        return render_template('verify.html', title="Verify",
                               code=veri_code, result=v.error)
    else:
        return redirect('/user/%s' % veri_code)


@app.route('/recover', methods=['GET', 'POST'])
def recovery():
    form = recover.RecoverForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
        response = recover.do_recover(form.email.data)
        if response:
            flash(response['response'], 'ok')
        else:
            flash('This email does not have an account.', 'error')
        return render_template('recover.html', title="Recover",
                               recover_active='active', form=form)
    else:
        return render_template('recover.html', title="Recover",
                               recover_active='active', form=form,
                               show_form=True)


@app.route('/user/<userid>')
def userpage(userid):
    return render_template('userpage.html', title='User Page',
                           userid=userid)

# TODO: Implement user's home page to get their bookmark

@app.route('/user/<userid>/send', methods=['POST'])
def send(userid):
    if not isinstance(userid, unicode):
        abort(401)
    elif not userid.isalnum():
        abort(401)
    elif not len(userid) == 40:
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
            return jsonify({'status': {'error': e.message}}), 500
        else:
            return jsonify(status='OK')


@app.errorhandler(404)
def fourohfour(error):
    return render_template('404.html'), 404
