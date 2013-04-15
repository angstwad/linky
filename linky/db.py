import sqlalchemy.exc
import sqlalchemy.orm.exc

import exc

from datetime import datetime
from collections import namedtuple

from config import MAX_EMAILS_PER_DAY
from db_def import Session, user_register, user_verified, emails_sent
from gen_hash import gen_sha_hash
from . import logger


class register(object):
    def __init__(self, email):
        self.session = Session()
        self.email = email

    def __insert_reg_db(self, userhash):
        logger.info('Beginning insert of %s into user_register DB.'
                    % self.email)
        new_user = user_register(email=self.email, send_key=userhash,
                                 create_time=datetime.utcnow(),
                                 last_login=datetime.utcnow())
        self.session.add(new_user)

        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            logger.warning('Duplicate email found in '
                           'user_registered table: %s' % self.email)
            logger.exception(e.message)
        except Exception as e:
            logger.exception(e.message)
        else:
            logger.info('Email registered, written to DB: %s' % self.email)
            return {'email': self.email,
                    'hash': userhash}

    def __in_verified_db(self):
        logger.info('Checking verified DB for email %s.' % self.email)
        if self.session.query(user_verified)\
                       .filter_by(email=self.email)\
                       .count() > 0:
            pass
        else:
            return True

    def do_register(self):
        logger.info('Attempt to register email: %s' % self.email)
        if not self.__in_verified_db():
            userhash = gen_sha_hash(self.email)
            return self.__insert_reg_db(userhash)

    def recover(self):
        q_ver = self.session.query(user_verified)\
                    .filter_by(email=self.email)\
                    .first()
        if q_ver:
            return {'email': q_ver.email,
                    'key': q_ver.email_key}
        else:
            q_reg = self.session.query(user_register)\
                                .filter_by(email=self.email)\
                                .first()
            if q_reg:
                return {'email': q_reg.email,
                        'key': q_reg.send_key}


class verification(object):
    def __init__(self, key):
        self.key = key
        self.session = Session()

    def check_verification(self):
        try:
            logger.info('Check if verified key %s' % self.key)
            q = self.session.query(user_verified).filter_by(email_key=self.key).one()
        except sqlalchemy.orm.exc.MultipleResultsFound or sqlalchemy.orm.exc.NoResultFound as e:
            logger.exception(e.message)
            return False
        else:
            logger.info('Checked key, user is verified: %s' % q.email)
            return True

    def run_verification(self):
        try:
            logger.info('Verify key %s' % self.key)
            q = self.session.query(user_register).filter_by(send_key=self.key).one()
        except sqlalchemy.orm.exc.NoResultFound or sqlalchemy.orm.exc.MultipleResultsFound as e:
            logger.exception(e.message)
        else:
            if self._reg_db_to_ver_db(q):
                return True

    def _reg_db_to_ver_db(self, q):
        new_record = user_verified(email=q.email, email_key=q.send_key)
        try:
            logger.info('Attempting to add record to verify DB: %s, %s' % (q.email, q.send_key))
            self.session.add(new_record)
        except BaseException as e:
            logger.exception(e.message)
        else:
            logger.info('Record added to verify DB: %s, %s' % (q.email, q.send_key))
            try:
                logger.info('Attempting to delete record from register DB: %s' % q.email)
                self.session.delete(q)
            except Exception as e:
                logger.exception(e.message)
            else:
                logger.info('Record deleted, purging from DB with session.commit(): %s' % q.email)
                self.session.commit()
                return True


class mail(object):
    def __init__(self, key):
        self.key = key
        self.session = Session()

        try:
            q = self.session.query(user_verified).filter_by(email_key=key).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exc.UserNotFoundException('Key not found in DB: %s' % self.key)
        except sqlalchemy.orm.exc.MultipleResultsFound as e:
            logger.exception(e.message)
        else:
            self.email_addr = q.email
            self.__sendkey = q.email_key

    def can_send(self):
        def requery():
            try:
                logger.info('Requery for key: %s', self.key)
                self.q = self.session.query(emails_sent).filter_by(email_key=self.key).one()
            except sqlalchemy.orm.exc.NoResultFound or sqlalchemy.orm.exc.MultipleResultsFound as e:
                logger.exception(e.message)

        try:
            logger.info('Looking for user in emails_sent DB: %s' % self.email_addr)
            self.q = self.session.query(emails_sent).filter_by(email_key=self.key).one()
        except sqlalchemy.orm.exc.NoResultFound:
            logger.info('Email has no entry in emails_sent DB: %s' % self.email_addr)
            self.session.add(emails_sent(email=self.email_addr, email_key=self.__sendkey, num_sent=0))
            requery()
        except sqlalchemy.orm.exc.MultipleResultsFound as e:
            logger.exception(e.message)
            return False
        finally:
            if self.q.num_sent <= MAX_EMAILS_PER_DAY:
                logger.info('User under email limit of %d: %s' % (MAX_EMAILS_PER_DAY, self.email_addr))
                return True
            else:
                return False

    def plus_one(self):
        logger.info('Email send count increased for %s to %d', self.q.email, self.q.num_sent)
        if self.q.num_sent is not None:
            self.q.num_sent += 1
        else:
            self.q.num_sent = 1
        self.session.add(self.q)
        self.session.commit()
