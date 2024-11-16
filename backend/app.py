import json
import time
from flask_cors import CORS
from datetime import timedelta
import os
from backend.Model import db, SQLALCHEMY_DATABASE_URI, SCOPES
from backend import Model
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import redis
from flask import Flask
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

CORS(app, supports_credentials=True)


# start google drive api service
def start_drive_api_service():
    from backend.Model import TokenModel
    # find token
    token = TokenModel.query.first()
    # check the token is existed
    if token:
        try:
            # load token to get credentials
            creds = Credentials.from_authorized_user_info(json.loads(token.token), SCOPES)

            # Check if the credentials have expired but can be refreshed
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                try:
                    token.token = creds.to_json()
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
            # build service once get a valid credentials
            Model.drive_service = build("drive", "v3", credentials=creds)
            print('Drive Service is created successfully')
        # handle error and exception
        except HttpError as error:
            print(f"An error occurred: {error}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print('Token cannot be found')


# set the number of thread pool executor
def set_number_of_executor():
    from backend.Model import PullingConfigurationModel
    configs = PullingConfigurationModel.query.all()
    # check the number of configuration in the database  and set the number
    if len(configs) >= 5:
        Model.thread_worker_count = len(configs) + 3


# get the configuration and start to pull data that in the database
def load_existing_configurations():
    from backend.Model import PullingConfigurationModel
    from pullingConfiguration import pull_data_in_background
    configs = PullingConfigurationModel.query.all()
    for config in configs:
        Model.executor.submit(pull_data_in_background, config.id)
        Model.current_thread_worker_count += 1


# initialise database
db.init_app(app)

# Redis connection to store task metadata
redis_client = redis.Redis.from_url(app.config['REDIS_URL'])


# check the google drive api credential and token whether is valid in background
def check_credentials_valid():
    from backend.Model import TokenModel
    with app.app_context():
        # redis store task and status
        redis_client.hset('check_credentials_task', 'status', 'running')
        while True:
            # find token
            token = TokenModel.query.first()
            # if the token is existed
            if token:
                try:
                    # load token
                    creds = Credentials.from_authorized_user_info(json.loads(token.token), SCOPES)
                    # Check if the credentials have expired but can be refreshed
                    if creds and creds.expired and creds.refresh_token:
                        try:
                            creds.refresh(Request())
                            token.token = creds.to_json()
                            db.session.commit()
                            Model.drive_service = build("drive", "v3", credentials=creds)
                        except Exception as e:
                            db.session.rollback()

                    redis_client.hset('check_credentials_task', 'status', 'running')
                # handle error and exception
                except HttpError as error:
                    redis_client.hset('check_credentials_task', 'status', 'error')
                    print(f"An error occurred: {error}")
                except Exception as e:
                    redis_client.hset('check_credentials_task', 'status', 'error')
                    print(f"An error occurred: {e}")
            else:
                redis_client.hset('check_credentials_task', 'status', 'error')
            time.sleep(20)


def startAll():
    from backend.SystemBoundary import SystemBoundary
    with app.app_context():
        # create table structure
        db.create_all()

        # register blue print
        app.register_blueprint(SystemBoundary)

        # initialise the thread pool and process pool executor
        set_number_of_executor()
        Model.executor = ThreadPoolExecutor(max_workers=Model.thread_worker_count)
        Model.process_executor = ProcessPoolExecutor(max_workers=Model.process_worker_count)

        # start service
        start_drive_api_service()

        # use threading to perform check credentials
        thread = threading.Thread(target=check_credentials_valid, args=())
        thread.start()

        # load configuration
        load_existing_configurations()


startAll()


# main method
if __name__ == '__main__':
    app.run(debug=True)
