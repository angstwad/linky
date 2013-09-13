import sqlalchemy.exc
import sqlalchemy.orm.exc
import exc
import gen_key
from config import MAX_EMAILS_PER_DAY
from db_def import Session, UserRegister, UserVerified, EmailsSent
from . import app


class Register(object):
    def __init__(self, email):
        self.session = Session()
        self.email = email

    def do_register(self):
        app.logger.info('Beginning register of email: %s' % self.email)
        if not self.__in_verified_db():
            key = gen_key.generate(self.email)
            return self.__insert_reg_db(key)

    def __in_verified_db(self):
        app.logger.info('Checking verified DB for email %s.' % self.email)
        if self.session.query(UserVerified)\
                       .filter_by(email=self.email)\
                       .count() > 0:
            app.logger.info('Registration fail, found in verified DB: %s'
                        % self.email)
            self.error = "Email has already been verified."
            return True

    def __insert_reg_db(self, key):
        app.logger.info('Beginning insert of %s into user_register DB.'
                    % self.email)
        new_user = UserRegister(email=self.email, send_key=key)
        self.session.add(new_user)

        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            self.error = "Email has already been registered."
            app.logger.info('Duplicate email found in '
                        'user_registered table: %s' % self.email)
            return False
        except Exception as e:
            app.logger.exception(e.message)
        else:
            app.logger.info('Email registered, written to DB: %s' % self.email)
            self.key = key
            return True

    def recover(self):
        q_ver = self.session.query(UserVerified)\
                    .filter_by(email=self.email)\
                    .first()
        if q_ver:
            return {'status': 'verified',
                    'email': q_ver.email,
                    'key': q_ver.email_key}
        else:
            q_reg = self.session.query(UserRegister)\
                                .filter_by(email=self.email)\
                                .first()
            if q_reg:
                return {'status': 'registered',
                        'email': q_reg.email,
                        'key': q_reg.send_key}


class Verification(object):
    def __init__(self, key):
        self.key = key
        self.session = Session()

    def check_verification(self):
        try:
            app.logger.info('Check if verified key %s' % self.key)
            q = self.session.query(UserVerified)\
                    .filter_by(email_key=self.key)\
                    .one()
        except (sqlalchemy.orm.exc.MultipleResultsFound,
                sqlalchemy.orm.exc.NoResultFound) as e:
            app.logger.exception(e.message)
            return False
        else:
            app.logger.info('Checked key, user is verified: %s' % q.email)
            return True

    def run_verification(self):
        try:
            app.logger.info('Verify key %s' % self.key)
            q = self.session.query(UserRegister)\
                    .filter_by(send_key=self.key)\
                    .one()
        except (sqlalchemy.orm.exc.NoResultFound,
                sqlalchemy.orm.exc.MultipleResultsFound) as e:
            app.logger.exception(e.message)
        else:
            if self.__move_to_verified(q):
                return True

    def __move_to_verified(self, q):
        new_record = UserVerified(email=q.email, email_key=q.send_key)
        app.logger.info('Attempting to add '
                    'record to verify DB: %s, %s' % (q.email, q.send_key))
        self.session.add(new_record)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            app.logger.info('Abort commit, key has already been verified: '
                        '%s' % self.key)
            self.error = 'Key has already been verified.'
            return True
        else:
            app.logger.info('Record added '
                        'to verify DB: %s, %s' % (q.email, q.send_key))
            return True


class Mail(object):
    def __init__(self, user_provided_key):
        self.user_provided_key = user_provided_key
        self.session = Session()

        try:
            q = self.session.query(UserVerified)\
                    .filter_by(email_key=user_provided_key)\
                    .one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exc.UserNotFoundException('Key not found in '
                                            'DB: %s' % self.user_provided_key)
        except sqlalchemy.orm.exc.MultipleResultsFound as e:
            app.logger.exception(e.message)
        else:
            self.email_addr = q.email
            self.key_from_db = q.email_key

    def can_send(self):
        def requery():
            try:
                app.logger.info('Requery for key: %s', self.user_provided_key)
                self.q = self.session.query(EmailsSent)\
                             .filter_by(email_key=self.user_provided_key)\
                             .one()
            except (sqlalchemy.orm.exc.NoResultFound,
                    sqlalchemy.orm.exc.MultipleResultsFound) as e:
                app.logger.exception(e.message)

        def insert_record(record):
            app.logger.info('Adding new record to emails_sent DB for email: %s'
                        % self.email_addr)
            self.session.add(record)
            try:
                app.logger.info('Committing transaction for new record, email %s'
                            % self.email_addr)
                self.session.commit()
            except Exception as e:
                app.logger.exception(e)

        try:
            app.logger.info('Looking for user in emails_sent table: %s'
                        % self.email_addr)
            self.q = self.session.query(EmailsSent)\
                         .filter_by(email_key=self.user_provided_key)\
                         .one()
        except sqlalchemy.orm.exc.NoResultFound:
            app.logger.info('Email has no entry in emails_sent table: %s'
                        % self.email_addr)
            record = EmailsSent(email=self.email_addr,
                                email_key=self.key_from_db,
                                num_sent=0)
            insert_record(record)
            requery()
        except sqlalchemy.orm.exc.MultipleResultsFound as e:
            app.logger.exception(e.message)
            return False
        else:
            app.logger.info('Result found in emails_sent table for email: %s'
                        % self.email_addr)
        finally:
            if self.q.num_sent <= MAX_EMAILS_PER_DAY:
                app.logger.info('User under email limit of '
                            '%d: %s' % (MAX_EMAILS_PER_DAY, self.email_addr))
                self.plus_one()
                return True
            else:
                return False

    def plus_one(self):
        if self.q.num_sent is not None:
            self.q.num_sent += 1
        else:
            self.q.num_sent = 1
        app.logger.info('Email send count increased for %s to %d'
                    % (self.q.email, self.q.num_sent))
        self.session.add(self.q)
        self.session.commit()
