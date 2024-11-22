import json
from flask import Blueprint, request, jsonify, session, redirect
from flask_cors import CORS
from backend.Controller import PullingConfiguration, TableConfiguration, TrainedMLAlgorithm, Task, SystemAdmin
from backend.Controller import SysLoginController, createPullingConfigurationController
from backend.Controller import viewPullingConfigurationController, editTableConfigurationController
from backend.Controller import createTableConfigurationController, viewTableConfigurationController
from backend.Controller import deleteTableConfigurationController, viewTrainedMLAlgorithmController
from backend.Controller import deleteTrainedMLAlgorithmController, editTrainedMLAlgorithmController, TrainMLAlgorithmController
from backend.Controller import deployTrainedMLAlgorithmController, ViewTaskController, EditPullingConfigurationController
from backend.Controller import DeletePullingConfigurationController, ViewModelTypeController
from backend.Controller import ViewFileController, GetModelStatusController, sysRenewController
from backend.Controller import EditTaskController, sysGetAccessController
from backend import Model
from backend.Model import db, SCOPES
import os
from googleapiclient.discovery import build
import re
from google_auth_oauthlib.flow import InstalledAppFlow

# create the boundary blueprint
SystemBoundary = Blueprint('SystemBoundary', __name__)
CORS(SystemBoundary, supports_credentials=True)

state = ''


# login api
@SystemBoundary.route('/Login', methods=['POST'])
def login():
    # get the data from frontend
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    # check the role whether is System Admin
    if role == 'System Admin':
        controller = SysLoginController()
        isValid = controller.login(username, password)

        # the credentials whether is valid
        if isValid:
            print(session)
            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401


# renew token api
@SystemBoundary.route('/renew', methods=['POST'])
def renewCredentials():
    try:
        global state
        controller = sysRenewController()
        data = controller.renew()
        state = data.get('state')
        return jsonify(data), 200
    except Exception as e:
        print(e)
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")
            print("Credentials file removed")
        return jsonify({"error": str(e)}), 500


@SystemBoundary.route('/callbackR', methods=['GET'])
def callbackR():
    from backend.Model import TokenModel
    try:
        code = request.args.get('code')

        if not code:
            return redirect('https://traffic-frontend-ip3j.onrender.com/renew?status=failed')

        # use credentials to get the drive access
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes=SCOPES,
                                                         state=request.args.get('state'),
                                                         redirect_uri='https://traffic-backend-n4iz.onrender.com/callbackR')
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        try:
            # store the token to database
            token = TokenModel.query.first()
            token.token = credentials.to_json()
            db.session.commit()
            # re-build the drive service
            Model.drive_service = build("drive", "v3", credentials=credentials)
            return redirect('https://traffic-frontend-ip3j.onrender.com/renew?status=success')
        except Exception as e:
            db.session.rollback()
            return redirect('https://traffic-frontend-ip3j.onrender.com/renew?status=failed')
        finally:
            if os.path.exists("credentials.json"):
                os.remove("credentials.json")
                print("Credentials file removed")
    except Exception as e:
        print(e)
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")
            print("Credentials file removed")
        return redirect('https://traffic-frontend-ip3j.onrender.com/renew?status=failed')


# get the google drive service access
@SystemBoundary.route('/getGoogleAccess', methods=['POST'])
def get_access_credentials():
    try:
        global state
        controller = sysGetAccessController()
        data = controller.get_access_credentials()
        state = data.get('state')
        return jsonify(data), 200
    except Exception as e:
        print(e)
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")
            print("Credentials file removed")
        return jsonify({"error": str(e)}), 500


@SystemBoundary.route('/callbackG', methods=['GET'])
def callback():
    try:
        code = request.args.get('code')

        if not code:
            return redirect('https://traffic-frontend-ip3j.onrender.com/getDriveServiceAccess?status=failed')

        # use credentials to get the drive access
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes=SCOPES,
                                                         state=request.args.get('state'),
                                                         redirect_uri='https://traffic-backend-n4iz.onrender.com/callbackG')
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        # build the system admin google drive service
        Model.sys_service = build('drive', 'v3', credentials=credentials)

        # delete local credentials.json
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")
            print("Credentials file removed")

        print('System Admin service is created successfully')
        return redirect('https://traffic-frontend-ip3j.onrender.com/getDriveServiceAccess?status=success')
    except Exception as e:
        print(e)
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")
            print("Credentials file removed")
        return redirect('https://traffic-frontend-ip3j.onrender.com/getDriveServiceAccess?status=failed')


# logout
@SystemBoundary.route('/logout', methods=['POST'])
def logout():
    # clear the session
    session.clear()
    # set the system admin drive service to none
    Model.sys_service = None
    return jsonify({"message": "Logout successful!"}), 200


# convert the input to pattern that can convert to json format
def fix_string(ss):
    return re.sub(r'(\b\w+\b):\s*([^,}]+)', r'"\1": "\2"', ss)


# add new pulling data configuration
@SystemBoundary.route('/addPull', methods=['POST'])
def addNewPullingConfiguration():
    try:
        # get the data from frontend
        data = request.get_json()
        # handle header and params input
        if data.get('header').strip() == '' or not data.get('header').strip():
            ori_header = '{}'
        else:
            ori_header = data.get('header')

        if data.get('params').strip() == '' or not data.get('params').strip():
            ori_params = '{}'
        else:
            ori_params = data.get('params')

        # convert the pattern
        fixed_header = fix_string(ori_header)
        fixed_params = fix_string(ori_params)

        # convert the header and params to json format
        name = data.get('name')
        description = data.get('description')
        data_source = data.get('data_source')
        header = json.loads(fixed_header)
        frequency_min = int(data.get('frequency_min'))
        params = json.loads(fixed_params)

        if not description or not description.strip():
            description = None

        # create a pulling configuration instance
        configuration = PullingConfiguration(
            name=name,
            description=description,
            data_source=data_source,
            header=header,
            frequency_min=frequency_min,
            params=params
        )

        CreatePullingConfigurationController = createPullingConfigurationController()
        # add new pulling configuration
        isSuccess = CreatePullingConfigurationController.addNewPullingConfiguration(configuration)
        # check add new configuration whether is successful
        if isSuccess:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 400
    # handle error and exception and return false
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 402


# view the pulling data configuration
@SystemBoundary.route('/viewPull', methods=['GET'])
def viewPullingConfiguration():
    # get the data and return to frontend
    viewPullController = viewPullingConfigurationController()
    data = viewPullController.viewPullingConfiguration()
    return jsonify(data)


# edit pulling data configuration
@SystemBoundary.route('/editPullConfig', methods=['PUT'])
def editPullingConfiguration():
    try:
        # get the data from frontend
        data = request.get_json()

        # handle the header and params input
        ori_header = f'{data.get("header")}'
        ori_params = f'{data.get("params")}'

        # convert the pattern
        fixed_header = fix_string(ori_header)
        fixed_params = fix_string(ori_params)

        id = int(data.get('id'))
        name = data.get('name')
        description = data.get('description')
        data_source = data.get('data_source')
        header = json.loads(fixed_header)
        frequency_min = int(data.get('frequency_min'))
        params = json.loads(fixed_params)

        if not description or not description.strip():
            description = None

        configuration = PullingConfiguration(
            id=id,
            name=name,
            description=description,
            data_source=data_source,
            header=header,
            frequency_min=frequency_min,
            params=params
        )

        # edit the pulling data configuration
        editPullingConfigurationController = EditPullingConfigurationController()
        isSuccess = editPullingConfigurationController.editPullingConfiguration(configuration)
        # check the edit whether is successful
        if isSuccess:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 400
    # handle exception and error and return false
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 402


# delete pulling data configuration
@SystemBoundary.route('/deletePull', methods=['DELETE'])
def deletePullingConfiguration():
    try:
        # get the data from frontend
        data = request.args
        id = int(data.get('id'))
        configuration = PullingConfiguration(id=id)

        # delete the configuration
        deletePullingConfigurationController = DeletePullingConfigurationController()
        isSuccess = deletePullingConfigurationController.deletePullingConfiguration(configuration)
        # check delete whether is successful
        if isSuccess:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 400
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 402


# add new table configuration
@SystemBoundary.route('/addTableConfig', methods=['POST'])
def addNewTableConfiguration():
    # get the data from frontend
    data = request.get_json()

    # handle hyper parameters input
    if data.get('hyper_parameters').strip() == '' or not data.get('hyper_parameters').strip():
        ori_params = '{}'
    else:
        ori_params = data.get('hyper_parameters')

    # convert pattern
    fixed_params = fix_string(ori_params)

    name = data.get('name')
    description = data.get('description')
    file_id = data.get('file_id')
    file_name = data.get('file_name')
    columns = data.get('columns')
    columns = columns.split(',')
    model_type_id = data.get('model_type_id')
    hyper_parameters = json.loads(fixed_params)

    if not description or not description.strip():
        description = None

    configuration = TableConfiguration(name=name, description=description,
                                       file_id=file_id, file_name=file_name,
                                       columns=columns,
                                       model_type_id=model_type_id,
                                       hyper_parameters=hyper_parameters)

    # add new table configuration
    CreateTableConfigurationController = createTableConfigurationController()
    isSuccess = CreateTableConfigurationController.addNewTableConfiguration(configuration)
    # check add configuration whether is successful
    if isSuccess:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 400


# view table configuration
@SystemBoundary.route('/viewTable', methods=['GET'])
def viewTableConfiguration():
    # get data and return to frontend
    ViewTableConfiguration = viewTableConfigurationController()
    data = ViewTableConfiguration.viewTableConfiguration()
    return jsonify(data)


# edit table configuration
@SystemBoundary.route('/editTableConfig', methods=['PUT'])
def editTableConfiguration():
    try:
        # get the data from frontend
        data = request.get_json()
        ori_params = f'{data.get("hyper_parameters")}'
        # convert pattern
        fixed_params = fix_string(ori_params)
        print(data.get('columns'))
        for column in data.get('columns'):
            print(column)
        id = int(data.get('id'))
        name = data.get('name')
        description = data.get('description')
        file_id = data.get('file_id')
        file_name = data.get('file_name')
        columns = data.get('columns')
        model_type_id = int(data.get('model_type_id'))
        hyper_parameters = json.loads(fixed_params)

        if not description or not description.strip():
            description = None

        configuration = TableConfiguration(id=id, name=name, description=description,
                                           file_id=file_id, file_name=file_name,
                                           columns=columns,
                                           model_type_id=model_type_id,
                                           hyper_parameters=hyper_parameters)

        # edit configuration
        EditTableConfigurationController = editTableConfigurationController()
        isSuccess = EditTableConfigurationController.editTableConfiguration(configuration)
        # check edit whether is successful
        if isSuccess:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 400
    # handle error and exception and return false
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 402


# delete table configuration
@SystemBoundary.route('/deleteTableConfig', methods=['DELETE'])
def deleteTableConfiguration():
    # get the data from frontend
    data = request.args
    id = data.get('id')
    configuration = TableConfiguration(id=id)

    # delete the table configuration
    DeleteTableConfigurationController = deleteTableConfigurationController()
    isSuccess = DeleteTableConfigurationController.deleteTableConfiguration(configuration)
    # check delete whether is successful
    if isSuccess:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 400


# view the model type
@SystemBoundary.route('/viewModelType', methods=['GET'])
def viewModelType():
    # get the data and return to frontend
    viewModelTypeController = ViewModelTypeController()
    data = viewModelTypeController.viewModelType()
    return jsonify(data)


# view the file
@SystemBoundary.route('/viewFile', methods=['GET'])
def viewFile():
    # get the data and return to frontend
    viewFileController = ViewFileController()
    data = viewFileController.viewFile()
    return jsonify(data)


# train model
@SystemBoundary.route('/trainModel', methods=['POST'])
def trainModel():
    # get the data from frontend
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    table_configuration_id = data.get('table_configuration_id')

    if not description or not description.strip():
        description = None

    model = TrainedMLAlgorithm(name=name, description=description, table_configuration_id=table_configuration_id)

    # train model
    trainMLAlgorithmController = TrainMLAlgorithmController()
    isSuccess = trainMLAlgorithmController.trainModel(model)
    # check the training setup whether is successful
    if isSuccess:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 400


# get the model status
@SystemBoundary.route('/getModelStatus', methods=['GET'])
def getModelStatus():
    # get the data and return to frontend
    getModelStatusController = GetModelStatusController()
    data = getModelStatusController.getModelStatus()
    return jsonify(data)


# view model
@SystemBoundary.route('/viewModel', methods=['GET'])
def viewTrainedMLAlgorithm():
    # get the data and return to frontend
    ViewTrainedMLAlgorithmController = viewTrainedMLAlgorithmController()
    data = ViewTrainedMLAlgorithmController.viewTrainedMLAlgorithm()
    return jsonify(data)


# edit the model details
@SystemBoundary.route('/editModel', methods=['PUT'])
def editTrainedMLAlgorithm():
    # get the data from frontend
    data = request.get_json()
    id = int(data.get('id'))
    description = data.get('description')

    if not description or not description.strip():
        description = None

    model = TrainedMLAlgorithm(id=id, description=description)

    # edit model
    EditTrainedMLAlgorithmController = editTrainedMLAlgorithmController()
    isSuccess = EditTrainedMLAlgorithmController.editTrainedMLAlgorithm(model)
    # check edit whether is successful
    if isSuccess:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 400


# delete the model
@SystemBoundary.route('/deleteModel', methods=['DELETE'])
def deleteTrainedMLAlgorithm():
    # get the data from frontend
    data = request.args
    id = int(data.get('id'))
    model = TrainedMLAlgorithm(id=id)

    DeleteTrainedMLAlgorithmController = deleteTrainedMLAlgorithmController()
    # delete model
    isSuccess = DeleteTrainedMLAlgorithmController.deleteTrainedMLAlgorithm(model)
    # check delete whether is successful
    if isSuccess:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 400


# deploy model
@SystemBoundary.route('/deployModel', methods=['PUT'])
def deployTrainedMLAlgorithm():
    # get the data from frontend
    data = request.get_json()
    id = int(data.get('id'))
    name = data.get('name')
    description = data.get('description')
    train_model_id = int(data.get('train_model_id'))
    file_id = data.get('file_id')
    file_name = data.get('file_name')
    task_type = data.get('task_type')

    task = Task(id=id, name=name, description=description,
                train_model_id=train_model_id, file_id=file_id,
                file_name=file_name, task_type=task_type)

    # deploy model to task
    DeployTrainedMLAlgorithmController = deployTrainedMLAlgorithmController()
    isSuccess = DeployTrainedMLAlgorithmController.deployTrainedMLAlgorithm(task)
    # check deploy model whether is successful
    if isSuccess:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 400


# edit task
@SystemBoundary.route('/editTask', methods=['PUT'])
def editTask():
    # get the data from frontend
    data = request.get_json()
    id = int(data.get('id'))
    description = data.get('description')
    file_id = data.get('file_id')
    file_name = data.get('file_name')
    task_type = data.get('task_type')

    if not description or not description.strip():
        description = None

    task = Task(id=id, description=description, file_id=file_id,
                file_name=file_name, task_type=task_type)
    # edit task
    editTaskController = EditTaskController()
    isSuccess = editTaskController.editTask(task)
    # check edit whether is successful
    if isSuccess:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 400


# view task
@SystemBoundary.route('/ViewTask', methods=['GET'])
def viewTask():
    # get the data and return to frontend
    viewTaskController = ViewTaskController()
    data = viewTaskController.viewTask()
    return jsonify(data)