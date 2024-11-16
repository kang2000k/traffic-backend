import os
import importlib.util
import sys
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import Model
from Model import TaskModel, ModelTrainedModel, db
import io
import ast


# task class
class Task:
    # initialise method
    def __init__(self, id=None, name=None, description=None, train_model_id=None,
                 file_id=None, file_name=None, task_type=None):
        self.id = id
        self.name = name
        self.description = description
        self.train_model_id = train_model_id
        self.file_id = file_id
        self.file_name = file_name
        self.task_type = task_type

    # edit task
    @staticmethod
    def editTask(task):
        # get the instance
        tk = TaskModel.query.get(task.id)

        # check the instance is none
        if tk is None:
            return False

        try:
            tk.description = task.description
            tk.file_id = task.file_id
            tk.file_name = task.file_name
            tk.task_type = task.task_type

            # update the details
            db.session.commit()
            return True
        # handle exception and error and return false
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    # load the trained model
    @staticmethod
    def load_trained_model(modl):
        try:
            # find the load_model.py file
            file_name = 'load_model.py'
            folder_id = '1eZWgKXyZBqMUkw04VazUsUoH7omtOGdf'
            results = Model.sys_service.files().list(
                q=f"name='{file_name}' and '{folder_id}' in parents",
                spaces='drive',
                fields="files(id, name)"
            ).execute()
            files = results.get('files', [])
            # check the file whether is existed
            if not files:
                if os.path.exists(modl.model_file):
                    os.remove(modl.model_file)
                print('No load model files')
                return None

            # download the file to local
            file_id = files[0]['id']
            request = Model.sys_service.files().get_media(fileId=file_id)
            with open(file_name, 'wb') as file:
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Downloading {file_name}: {int(status.progress() * 100)}% complete")
            module_name = os.path.splitext(os.path.basename(file_name))[0]
            # Remove the module from sys.modules if it exists
            if module_name in sys.modules:
                del sys.modules[module_name]

            # Use importlib to import the downloaded module
            spec = importlib.util.spec_from_file_location(module_name, file_name)
            Module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = Module
            spec.loader.exec_module(Module)
            table_configuration = modl.table_configuration
            model_type = table_configuration.model_type
            model_type_name = model_type.type_name
            model_file = modl.model_file

            model = Module.load_model(model_type_name, model_file)
            if os.path.exists(modl.model_file):
                os.remove(modl.model_file)
            return model
        # handle error and exception and return none
        except HttpError as e:
            print(e)
            if os.path.exists(modl.model_file):
                os.remove(modl.model_file)
            return None
        except Exception as e:
            print(e)
            if os.path.exists(modl.model_file):
                os.remove(modl.model_file)
            return None

    # deploy trained model
    @staticmethod
    def deployTrainedMLAlgorithm(task):
        from app import app
        with app.app_context():
            accuracy_file = ''
            try:
                # get the task instance
                tk = TaskModel.query.get(task.id)
                # check the task whether is existed
                if tk:
                    train_model_id = task.train_model_id
                    trained_model = ModelTrainedModel.query.get(train_model_id)
                    # check the trained model id from user is existed
                    if trained_model:
                        folder_id = '1GIkCJZ4Ly6hsMyRiLgQsDzEUnd_1g42T'
                        model_file = trained_model.model_file
                        # find the file
                        results = Model.sys_service.files().list(
                            q=f"name='{model_file}' and '{folder_id}' in parents",
                            spaces='drive',
                            fields="files(id, name)"
                        ).execute()
                        model_files = results.get('files', [])
                        # check the model file whether is existed
                        if not model_files:
                            print(f"No file found with name '{model_file}'")
                            return False
                        else:
                            # download the model file to local
                            model_file_id = model_files[0]['id']
                            request = Model.sys_service.files().get_media(fileId=model_file_id)
                            with io.FileIO(model_file, 'wb') as fh:
                                downloader = MediaIoBaseDownload(fh, request)
                                done = False
                                while not done:
                                    status, done = downloader.next_chunk()
                            # load the trained model
                            model = Task.load_trained_model(trained_model)
                            # check the trained model whether is existed
                            if model:
                                # get the accuracy file
                                accuracy_file = f'{trained_model.name}_accuracy'
                                results = Model.sys_service.files().list(
                                    q=f"name='{accuracy_file}' and '{folder_id}' in parents",
                                    spaces='drive',
                                    fields="files(id, name)"
                                ).execute()
                                accuracy_files = results.get('files', [])
                                # check the accuracy file whether is existed
                                if not accuracy_files:
                                    print(f"No file found with name '{accuracy_file}_accuracy'")
                                    return False
                                else:
                                    # download accuracy file to local
                                    accuracy_file_id = accuracy_files[0]['id']
                                    request = Model.sys_service.files().get_media(fileId=accuracy_file_id)
                                    with io.FileIO(accuracy_file, 'wb') as fh:
                                        downloader = MediaIoBaseDownload(fh, request)
                                        done = False
                                        while not done:
                                            status, done = downloader.next_chunk()
                                    # check the task instance file id whether is none or empty string
                                    if not tk.file_id or tk.file_id == '':
                                        print("File id not found")
                                        if os.path.exists(accuracy_file):
                                            os.remove(accuracy_file)
                                        return False
                                    # get the accuracy and convert to float
                                    with open(accuracy_file, "r") as file:
                                        content = file.read()
                                    model_accuracy = ast.literal_eval(content)
                                    # do model validation
                                    model_task_type = trained_model.table_configuration.model_type.task_type

                                    # check the model whether is valid
                                    if model_task_type == tk.task_type:
                                        # update the details
                                        tk.train_model_id = task.train_model_id
                                        db.session.commit()
                                        if os.path.exists(accuracy_file):
                                            os.remove(accuracy_file)
                                        return True
                                    else:
                                        print("Model is not valid")
                                        if os.path.exists(accuracy_file):
                                            os.remove(accuracy_file)
                                        return False
                            else:
                                print("Model is not loaded")
                                return False
                    else:
                        print("Trained model is not found")
                else:
                    print("Task is not found")
                    return False
            # handle exception and error and return false
            except HttpError as error:
                print(error)
                if os.path.exists(accuracy_file):
                    os.remove(accuracy_file)
                db.session.rollback()
                return False
            except Exception as error:
                print(error)
                if os.path.exists(accuracy_file):
                    os.remove(accuracy_file)
                db.session.rollback()
                return False

    # view task
    @staticmethod
    def viewTask():
        # get the data and return list
        tasks = TaskModel.query.all()
        task_list = [
            {
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'train_model_id': task.train_model_id,
                'file_id': task.file_id,
                'file_name': task.file_name,
                'task_type': task.task_type
            }
            for task in tasks
        ]
        return task_list






