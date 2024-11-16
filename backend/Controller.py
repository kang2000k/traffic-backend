from systemAdmin import SystemAdmin
from pullingConfiguration import PullingConfiguration
from tableConfiguration import TableConfiguration
from trainedModel import TrainedMLAlgorithm
from task import Task
from modelType import ModelType


# system admin login controller
class SysLoginController:
    def __init__(self):
        self.systemAdmin = SystemAdmin()

    def login(self, username, password):
        return self.systemAdmin.login(username, password)


# system admin renew token controller
class sysRenewController:
    def __init__(self):
        self.systemAdmin = SystemAdmin()

    def renew(self):
        return self.systemAdmin.renew_credentials()


# system admin renew token controller
class sysGetAccessController:
    def __init__(self):
        self.systemAdmin = SystemAdmin()

    def get_access_credentials(self):
        return self.systemAdmin.get_access_credentials()


# create pulling data configuration controller
class createPullingConfigurationController:
    def addNewPullingConfiguration(self, configuration):
        return PullingConfiguration.add_configuration(configuration)


# view pulling data configuration controller
class viewPullingConfigurationController:
    def viewPullingConfiguration(self):
        return PullingConfiguration.viewPullingConfiguration()


# edit pulling data configuration controller
class EditPullingConfigurationController:
    def editPullingConfiguration(self, configuration):
        return PullingConfiguration.editPullingConfiguration(configuration)


# delete pulling data configuration controller
class DeletePullingConfigurationController:
    def deletePullingConfiguration(self, configuration):
        return PullingConfiguration.deletePullingConfiguration(configuration)


# create specific table configuration controller
class createTableConfigurationController:
    def addNewTableConfiguration(self, configuration):
        return TableConfiguration.addNewTableConfiguration(configuration)


# view specific table configuration controller
class viewTableConfigurationController:
    def viewTableConfiguration(self):
        return TableConfiguration.viewTableConfiguration()


# edit specific table configuration controller
class editTableConfigurationController:
    def editTableConfiguration(self, configuration):
        return TableConfiguration.editTableConfiguration(configuration)


# delete specific table configuration controller
class deleteTableConfigurationController:
    def deleteTableConfiguration(self, configuration):
        return TableConfiguration.deleteTableConfiguration(configuration)


# view pulled data file controller
class ViewFileController:
    def viewFile(self):
        return TableConfiguration.list_csv_file()


# view model type controller
class ViewModelTypeController:
    def viewModelType(self):
        return ModelType.viewModelType()


# train model controller
class TrainMLAlgorithmController:
    def trainModel(self, model):
        return TrainedMLAlgorithm.trainModel(model)


# view model status controller
class GetModelStatusController:
    def getModelStatus(self):
        return TrainedMLAlgorithm.getModelStatus()


# view trained model controller
class viewTrainedMLAlgorithmController:
    def viewTrainedMLAlgorithm(self):
        return TrainedMLAlgorithm.viewTrainedMLAlgorithm()


# edit trained model controller
class editTrainedMLAlgorithmController:
    def editTrainedMLAlgorithm(self, model):
        return TrainedMLAlgorithm.editTrainedMLAlgorithm(model)


# delete trained model controller
class deleteTrainedMLAlgorithmController:
    def deleteTrainedMLAlgorithm(self, model):
        return TrainedMLAlgorithm.deleteTrainedMLAlgorithm(model)


# deploy trained model controller
class deployTrainedMLAlgorithmController:
    def deployTrainedMLAlgorithm(self, task):
        return Task.deployTrainedMLAlgorithm(task)


# edit task controller
class EditTaskController:
    def editTask(self, task):
        return Task.editTask(task)


# view task controller
class ViewTaskController:
    def viewTask(self):
        return Task.viewTask()
