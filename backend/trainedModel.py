from googleapiclient.errors import HttpError
from backend.Model import ModelTrainedModel, db
import io
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import pandas as pd
import os
import importlib.util
import sys
from backend import Model
from backend.app import redis_client


# model class
class TrainedMLAlgorithm:
    # initialise method
    def __init__(self, id=None, name=None, description=None, model_file=None,
                 created_date=None, table_configuration_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.model_file = model_file
        self.created_date = created_date
        self.table_configuration_id = table_configuration_id

    # train model
    @staticmethod
    def trainModel(model):
        from backend.app import app
        with app.app_context():
            from backend import Model
            try:
                new_model = ModelTrainedModel(
                    name=model.name,
                    description=model.description,
                    model_file='',
                    table_configuration_id=model.table_configuration_id
                )
                # add the model to database
                db.session.add(new_model)
                db.session.commit()

                model_id = new_model.id
                # perform task in background
                Model.process_executor.submit(train_model_background, model_id, Model.drive_service)
                return True
            # handle exception and erorr and return false
            except Exception as e:
                print(e)
                db.session.rollback()
                return False

    # download the algorithm
    @staticmethod
    def download_model_algorithm(file_name, service):
        from backend.app import app
        with app.app_context():
            try:
                # find the algorithm file
                folder_id = '1eZWgKXyZBqMUkw04VazUsUoH7omtOGdf'
                results = service.files().list(
                    q=f"name='{file_name}' and '{folder_id}' in parents",
                    spaces='drive',
                    fields="files(id, name)"
                ).execute()

                files = results.get('files', [])
                # check the file whether is existed
                if not files:
                    return None

                # download the file
                file_id = files[0]['id']
                request = service.files().get_media(fileId=file_id)
                with open(file_name, 'wb') as file:
                    downloader = MediaIoBaseDownload(file, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f"Downloading {file_name}: {int(status.progress() * 100)}% complete")
                return file_name
            # handle error and exception and return none
            except HttpError as e:
                return None
            except Exception as e:
                return None

    # import the algorithm
    @staticmethod
    def import_downloaded_algo(file):
        from backend.app import app
        with app.app_context():
            # Remove the .py extension to get the module name
            module_name = os.path.splitext(os.path.basename(file))[0]

            # Remove the module from sys.modules if it exists
            if module_name in sys.modules:
                del sys.modules[module_name]

            # Use importlib to import the downloaded module
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            return module

    # upload to google drive
    @staticmethod
    def upload_to_google_drive(model_id, model_file, accuracy_file, metric_file, service):
        from backend.app import app
        with app.app_context():
            try:
                folder_id = '1GIkCJZ4Ly6hsMyRiLgQsDzEUnd_1g42T'

                # set the metadata
                file_metadata = {
                    'name': model_file,
                    'parents': [folder_id]
                }
                # Open the file in binary mode
                media = MediaFileUpload(model_file, mimetype='application/octet-stream')
                # Upload the file
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()

                # set the metadata
                file_metadata = {
                    'name': accuracy_file,
                    'parents': [folder_id]  # Specify the folder ID to upload into
                }
                # Open the file in binary mode
                media = MediaFileUpload(accuracy_file, mimetype='text/plain')
                # Upload the file
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()

                # set the metadata
                file_metadata = {
                    'name': metric_file,
                    'parents': [folder_id]  # Specify the folder ID to upload into
                }
                # Open the file in binary mode
                media = MediaFileUpload(accuracy_file, mimetype='text/plain')
                # Upload the file
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()

                trainedModel = ModelTrainedModel.query.get(model_id)
                if not trainedModel:
                    return False
                # update the trained model file
                trainedModel.model_file = model_file
                db.session.commit()
                return True
            # handle error and exception and return false
            except HttpError as e:
                db.session.rollback()
                return False
            except Exception as e:
                db.session.rollback()
                return False

    # View all trained models
    @staticmethod
    def viewTrainedMLAlgorithm():
        # get the data ad return list
        models = ModelTrainedModel.query.all()
        model_list = [
            {
                'id': model.id,
                'name': model.name,
                'description': model.description,
                'model_file': model.model_file,
                'created_date': model.created_date,
                'table_configuration_id': model.table_configuration_id,

            }
            for model in models
        ]
        return model_list

    # update trained model
    @staticmethod
    def editTrainedMLAlgorithm(model):
        # get the instance
        trainedModel = ModelTrainedModel.query.get(model.id)

        # check the instance whether is existed
        if not trainedModel:
            return False

        trainedModel.description = model.description
        try:
            # update the database
            db.session.commit()
            return True
        # handle exception and error and return false
        except Exception as e:
            db.session.rollback()
            return False

    # delete trained model
    @staticmethod
    def deleteTrainedMLAlgorithm(model):
        # get the instance
        trainedModel = ModelTrainedModel.query.get(model.id)

        # check the instance whether is existed or is deployed by tasks
        if (not trainedModel) and trainedModel.tasks:
            return False

        try:
            # delete instance
            db.session.delete(trainedModel)
            db.session.commit()
            return True
        # handle exception and error and return false
        except Exception as e:
            db.session.rollback()
            return False

    # get the model status
    @staticmethod
    def getModelStatus():
        from backend.app import app
        with app.app_context():
            # query the model
            models = ModelTrainedModel.query.all()
            status_list = []
            for model in models:
                model_id = model.id
                # find the redis task details
                if redis_client.exists(f'train_model_task:{model_id}'):
                    status = redis_client.hget(f'train_model_task:{model_id}', 'status')
                    message = redis_client.hget(f'train_model_task:{model_id}', 'message')

                    if status is None:
                        status = ''
                    else:
                        status = status.decode('utf-8')

                    if message is None:
                        message = ''
                    else:
                        message = message.decode('utf-8')

                    # return list
                    status_list.append({
                        'id': model.id,
                        'status': status,
                        'message': message
                    })
            return status_list


# train model in background
def train_model_background(model_id, service):
    from backend.app import app
    with ((app.app_context())):
        try:
            # create and set the redis task details and status
            redis_client.hset(f'train_model_task:{model_id}', 'status', 'running')
            model = ModelTrainedModel.query.get(model_id)

            # check the instance whether is none
            if model is None:
                redis_client.hset(f'train_model_task:{model_id}', 'status', 'error')
                redis_client.hset(f'train_model_task:{model_id}', 'message', f'Model {model_id} is not found.')
                return

            # get and check the table configuration is none
            table_configuration = model.table_configuration
            if table_configuration is None:
                redis_client.hset(f'train_model_task:{model_id}', 'status', 'error')
                redis_client.hset(f'train_model_task:{model_id}', 'message', f'Model {model.name} table configuration is not found.')
                return

            # check the table configuration file id is none or empty string
            if table_configuration.file_id is None or table_configuration.file_id == '':
                redis_client.hset(f'train_model_task:{model_id}', 'status', 'error')
                redis_client.hset(f'train_model_task:{model_id}', 'message',
                                  f'Model {model.name} file id is not found.')
                return

            # Request to get the file metadata
            request = service.files().export(fileId=table_configuration.file_id, mimeType='text/csv')
            file_stream = io.BytesIO(request.execute())
            file_stream.seek(0)

            # Load the CSV file content into a DataFrame
            df = pd.read_csv(file_stream)
            if (table_configuration.columns and table_configuration.columns != []
                    and table_configuration.columns != {} and table_configuration.columns != ['']):
                df = df[table_configuration.columns]

            # download the algorithm from google drive
            model_type = table_configuration.model_type
            model_type_name = f'{model_type.type_name}.py'
            download_algo = TrainedMLAlgorithm.download_model_algorithm(model_type_name, service)
            # check algorithm whether is downloaded and imported successfully
            if download_algo:
                imported_algo = TrainedMLAlgorithm.import_downloaded_algo(download_algo)
                # get the saved model file and accuracy
                model_file, accuracy, metric = imported_algo.train_model(model.name, df, table_configuration.hyper_parameters)

                accuracy_file = f'{model.name}_accuracy'
                with open(accuracy_file, 'w') as f:
                    f.write(str(accuracy))

                metric_file = f'{model.name}_metric'
                with open(metric_file, 'w') as f:
                    f.write(str(metric))

                # upload the model file and accuracy file to google drive
                is_upload = TrainedMLAlgorithm.upload_to_google_drive(model.id, model_file, accuracy_file, metric_file, service)

                if os.path.exists(download_algo):
                    os.remove(download_algo)

                if os.path.exists(model_file):
                    os.remove(model_file)

                if os.path.exists(accuracy_file):
                    os.remove(accuracy_file)

                if os.path.exists(metric_file):
                    os.remove(metric_file)

                # check the upload whether is successful
                if is_upload:
                    redis_client.hset(f'train_model_task:{model_id}', 'status', 'OK')
                    redis_client.hset(f'train_model_task:{model_id}', 'message', f'Model {model.name} is Trained.')
                else:
                    redis_client.hset(f'train_model_task:{model_id}', 'status', 'error')
                    redis_client.hset(f'train_model_task:{model_id}', 'message', f'Model {model.name} is uploaded unsuccessfully.')
            else:
                redis_client.hset(f'train_model_task:{model_id}', 'status', 'error')
                redis_client.hset(f'train_model_task:{model_id}', 'message', f'Model {model.name} algorithm is not found.')
        # handle error and exception
        except HttpError as e:
            redis_client.hset(f'train_model_task:{model_id}', 'status', 'error')
            redis_client.hset(f'train_model_task:{model_id}', 'message', f'Model {model.name} {str(e)}')
        except Exception as e:
            redis_client.hset(f'train_model_task:{model_id}', 'status', 'error')
            redis_client.hset(f'train_model_task:{model_id}', 'message', f'Model {model.name} {str(e)}')
