# Copyright 2013 Paul Durivage <pauldurivage@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
import config
import log
from db_def import Session, create_db

app = Flask(__name__)
app.config.from_object(config)

logger = log.setup_custom_logger('root-logger')

# create_db()
from linky import routes


@app.teardown_request
def close_db(e):
    logger.info('Closing DB Session() on @app.teardown_request')
    Session.close_all()
