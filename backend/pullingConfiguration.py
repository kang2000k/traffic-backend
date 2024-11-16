import io
import pandas as pd
from pandas import json_normalize
import requests
import time
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from Model import PullingConfigurationModel, db, drive_service
import Model
from contextlib import contextmanager
from app import redis_client
from concurrent.futures import ThreadPoolExecutor


# pulling data configuration class
class PullingConfiguration:
    # initialise method
    def __init__(self, id=None, name=None, description=None, data_source=None,
                 header=None, frequency_min=None, last_pulled_at=None, created_date=None, params=None):
        self.id = id
        self.name = name
        self.description = description
        self.data_source = data_source
        self.header = header
        self.frequency_min = frequency_min
        self.last_pulled_at = last_pulled_at
        self.created_date = created_date
        self.params = params

    # lock method for using same resource tasks
    @staticmethod
    @contextmanager
    def distributed_lock(lock_name, timeout=60):
        lock = redis_client.lock(lock_name, timeout=timeout)
        acquired = lock.acquire(blocking=True)
        try:
            yield acquired
        finally:
            if acquired:
                lock.release()

    # View all pulling configuration
    @staticmethod
    def viewPullingConfiguration():
        configurations = PullingConfigurationModel.query.all()
        config_list = [
            {
                'id': configuration.id,
                'name': configuration.name,
                'description': configuration.description,
                'data_source': configuration.data_source,
                'headers': configuration.header,
                'frequency_min': configuration.frequency_min,
                'last_pulled_at': configuration.last_pulled_at,
                'created_date': configuration.created_date,
                'params': configuration.params
            }
            for configuration in configurations
        ]
        return config_list

    # update configuration
    @staticmethod
    def editPullingConfiguration(configuration):
        # get the configuration
        config = PullingConfigurationModel.query.get(configuration.id)

        if not config:
            return False

        # edit the value
        config.name = configuration.name
        config.description = configuration.description
        config.data_source = configuration.data_source
        config.header = configuration.header
        config.frequency_min = configuration.frequency_min
        config.params = configuration.params

        # commit and return true, and roll back if there has error and exception
        try:
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    # delete configuration
    @staticmethod
    def deletePullingConfiguration(configuration):
        # get the configuration
        config = PullingConfigurationModel.query.get(configuration.id)
        if not config:
            print("not found")
            return False

        try:
            # redis get the key and delete the details
            redis_key = f'pull_data_task:{config.id}'
            if redis_client.exists(redis_key):
                redis_client.delete(redis_key)

            # database delete record and return true
            db.session.delete(config)
            db.session.commit()
            return True
        # handle exception and return false
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    # add new configuration
    @staticmethod
    def add_configuration(configuration):
        from app import app
        with app.app_context():
            try:
                # check the current workers whether is equal or more than the total workers
                if Model.current_thread_worker_count >= Model.thread_worker_count:
                    # get the configurations
                    configurations = PullingConfigurationModel.query.all()
                    # change all the pulling task status to end
                    for config in configurations:
                        redis_key = f'pull_data_task:{config.id}'
                        if redis_client.exists(redis_key):
                            redis_client.hset(redis_key, 'status', 'end')

                    # shut down the executor
                    Model.executor.shutdown(wait=True)

                    # delete the task information in the redis
                    for config in configurations:
                        redis_key = f'pull_data_task:{config.id}'
                        if redis_client.exists(redis_key):
                            redis_client.delete(redis_key)

                    # add more workers
                    Model.thread_worker_count += 3

                    # re-initialise the executor
                    Model.executor = ThreadPoolExecutor(max_workers=Model.thread_worker_count)

                    # perform the task again
                    for config in configurations:
                        Model.executor.submit(pull_data_in_background, config.id)

                # add new configuration
                new_config = PullingConfigurationModel(
                    name=configuration.name,
                    description=configuration.description,
                    data_source=configuration.data_source,
                    header=configuration.header,
                    frequency_min=configuration.frequency_min,
                    params=configuration.params
                )
                # database add record
                db.session.add(new_config)
                db.session.commit()

                config_id = new_config.id

                # perform the task
                Model.executor.submit(pull_data_in_background, config_id)
                # current thread worker plus 1
                Model.current_thread_worker_count += 1
                return True
            # handle exception and return false
            except Exception as e:
                print(e)
                db.session.rollback()
                return False

    # get the redis task status
    @staticmethod
    def get_pull_task_status(config_id):
        status = redis_client.hget(f'pull_data_task:{config_id}', 'status')
        if status is None:
            return None
        return status.decode('utf-8')

    # find the file id by name
    @staticmethod
    def find_file_by_name(file_name, folder_id):
        try:
            # find the file id
            results = Model.drive_service.files().list(
                q=f"name='{file_name}' and '{folder_id}' in parents",
                spaces='drive',
                fields="files(id, name)"
            ).execute()

            files = results.get('files', [])
            # check the result if is not empty and return true
            if not files:
                print(f"No file found with name '{file_name}'")
                return pd.DataFrame()
            else:
                file_id = files[0]['id']
                print(f"Found file: {files[0]['name']} with ID: {file_id}")
                return PullingConfiguration.get_csv_file_content(file_id)
        # handle the exception and error and return false
        except HttpError as error:
            print(f"An error occurred: {error}")
            return pd.DataFrame()
        except Exception as error:
            print(f"An error occurred: {error}")
            return pd.DataFrame()

    # get the file content
    @staticmethod
    def get_csv_file_content(file_id):
        try:
            # Export Google Sheets file as CSV
            request = Model.drive_service.files().export(fileId=file_id, mimeType='text/csv')
            file_stream = io.BytesIO(request.execute())
            file_stream.seek(0)
            # Load the CSV file content into a DataFrame
            df = pd.read_csv(file_stream)
            print("File content loaded into DataFrame successfully.")
            return df
        # handle exception and error and return false
        except HttpError as error:
            print(f"An error occurred: {error}")
            return pd.DataFrame()
        except Exception as error:
            print(f"An error occurred: {error}")
            return pd.DataFrame()

    # upload the file to google drive
    @staticmethod
    def upload_csv_file(data, file_name):
        try:
            folder_id = '1f3xAKpfHcVmEaw7-TLX8EUjwiG2_vNQI'

            # convert data to dataframe
            df = pd.DataFrame(data)
            # get the old data
            old_df = PullingConfiguration.find_file_by_name(file_name, folder_id)
            # concat the pulled data and old data
            new_df = pd.concat([old_df, df], ignore_index=True)
            # remove the duplicate
            new_df.drop_duplicates(inplace=True)
            # Convert DataFrame to CSV in memory (without saving locally)
            csv_buffer = io.StringIO()
            new_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)  # Move cursor to the beginning of the stream

            # set the metadata
            file_metadata = {
                'name': f"{file_name}",
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [folder_id] if folder_id else None
            }

            # Locate the file by name and get its file ID
            query = f"name='{file_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
            results = Model.drive_service.files().list(q=query).execute()
            items = results.get('files', [])

            # check the file whether is existed
            if not items:
                # create new file and upload it with the data
                media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')
                file = Model.drive_service.files().create(body=file_metadata, media_body=media).execute()
                print(f"File '{file_name}' uploaded successfully to Google Drive with ID: {file['id']}")
            else:
                # use existing file to upload the data
                file_id = items[0]['id']
                media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')

                # Overwrite the file with new content
                updated_file = Model.drive_service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()

            # get the file with latest data again and drop duplicated to make sure no duplicated value
            new_df = PullingConfiguration.find_file_by_name(file_name, folder_id)
            new_df.drop_duplicates(inplace=True)

            csv_buffer = io.StringIO()
            new_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)  # Move cursor to the beginning of the stream

            query = f"name='{file_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
            results = Model.drive_service.files().list(q=query).execute()
            items = results.get('files', [])

            if items:
                file_id = items[0]['id']
                media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')

                # Overwrite the file with new content
                updated_file = Model.drive_service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()

                print(f"File {file_name}.csv updated successfully.")
            else:
                print(f"File {file_name}.csv cannot be found.")
        # handle exceptiobn and error and return false
        except HttpError as error:
            print(f"An error occurred: {error}")
        except Exception as error:
            print(f"An error occurred: {error}")


# pull data in the background
def pull_data_in_background(config_id):
    from app import app
    with app.app_context():
        # get the configuration by id
        config = PullingConfigurationModel.query.get(config_id)
        if config:
            try:
                # create and set the task and status to running
                redis_client.hset(f'pull_data_task:{config.id}', 'status', 'running')
                while True:
                    # every loop reset the database session to make sure the executor will get the latest value in database
                    with db.session() as session:
                        config = session.query(PullingConfigurationModel).get(config_id)
                        # check the task status whether is ended
                        if PullingConfiguration.get_pull_task_status(config.id) == 'end' or PullingConfiguration.get_pull_task_status(config.id) is None:
                            print(f'The config_id {config_id} is end.')
                            break

                        # check the task status whether is running
                        if PullingConfiguration.get_pull_task_status(config.id) == 'running':
                            # set the lock by the configuration name
                            with PullingConfiguration.distributed_lock(config.name):
                                # put in the details and call api
                                url = config.data_source
                                header = config.header or {}
                                payload = {}
                                params = config.params or {}
                                response = requests.request("GET", url, headers=header, data=payload, params=params)
                                # check the response status is valid
                                if response.status_code == 200:
                                    if "datamall" in url:
                                        data = response.json()['value']
                                    else:
                                        data = response.json()
                                    data = json_normalize(data)
                                    # upload to google drive
                                    PullingConfiguration.upload_csv_file(data, config.name)
                                else:
                                    print(f'The response is bad, {response.status_code}')
                            # the task will sleep based on the frequency minutes
                            time.sleep(config.frequency_min * 60)
            # handle exception and error and set the redis task status to error
            except Exception as e:
                print(f"Error occurred: {e}")
                redis_client.hset(f'pull_data_task:{config.id}', 'status', 'error')
        else:
            print(f'The config_id {config_id} cannot be found.')





