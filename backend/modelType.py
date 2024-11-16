from backend.Model import ModelTypeModel


# model type class
class ModelType:
    # Initialise method
    def __init__(self, id=None, type_name=None, task_type=None,
                 description=None, hyper_parameters=None):
        self.id = id
        self.type_name = type_name
        self.task_type = task_type
        self.description = description
        self.hyper_parameters = hyper_parameters

    # view all table configuration
    @staticmethod
    def viewModelType():
        modelTypes = ModelTypeModel.query.all()
        modelType_list = [
            {
                'id': modelType.id,
                'type_name': modelType.type_name,
                'task_type': modelType.task_type,
                'description': modelType.description,
                'hyper_parameters': modelType.hyper_parameters
            }
            for modelType in modelTypes
        ]
        return modelType_list
