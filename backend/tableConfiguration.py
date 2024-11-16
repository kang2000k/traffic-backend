from googleapiclient.errors import HttpError
from backend.Model import ModelTypeModel, TableConfigurationModel, db
from backend import Model


# table configuration class
class TableConfiguration:
    # initialise method
    def __init__(self, id=None, name=None, description=None, file_id=None, file_name=None,
                 columns=None, model_type_id=None, hyper_parameters=None, created_date=None):
        self.id = id
        self.name = name
        self.description = description
        self.file_id = file_id
        self.file_name = file_name
        self.columns = columns
        self.model_type_id = model_type_id
        self.hyper_parameters = hyper_parameters
        self.created_date = created_date

    # list the file
    @staticmethod
    def list_csv_file():
        try:
            csv_files = []
            # Pagination token, initially None
            page_token = None
            # get the list
            while True:
                folder_id = '1f3xAKpfHcVmEaw7-TLX8EUjwiG2_vNQI'
                results = Model.sys_service.files().list(
                    q=f"'{folder_id}' in parents",
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, webViewLink)",
                    pageToken=page_token  # Used to fetch the next page
                ).execute()
                # Get the list of CSV files from the response
                items = results.get("files", [])

                # check the files whether are existed
                if not items:
                    print("No CSV files found.")
                    break

                # Add the current page of CSV files to the csv_files list
                csv_files.extend(items)

                # Check if there is a next page token
                page_token = results.get('nextPageToken', None)
                if not page_token:
                    break

            # return name id and web link
            files = [
                {
                    'id': file['id'],
                    'name': file['name'],
                    'webViewLink': file['webViewLink']
                }
                for file in csv_files
            ]
            return files
        # handle error and exception and return empty list
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
        except Exception as error:
            print(f"An error occurred: {error}")
            return []

    # add new table configuration
    @staticmethod
    def addNewTableConfiguration(configuration):
        try:
            # check the hyperparameters is none and set the default parameters
            if configuration.hyper_parameters == {}:
                model_type = ModelTypeModel.query.filter_by(id=configuration.model_type_id).first()
                configuration.hyper_parameters = model_type.hyper_parameters

            new_config = TableConfigurationModel(
                name=configuration.name,
                description=configuration.description,
                file_id=configuration.file_id,
                file_name=configuration.file_name,
                columns=configuration.columns,
                model_type_id=configuration.model_type_id,
                hyper_parameters=configuration.hyper_parameters
            )
            # add to database
            db.session.add(new_config)
            db.session.commit()
            return True
        # handle exception and error and return false
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    # View all table configuration
    @staticmethod
    def viewTableConfiguration():
        # get the data and return list
        configurations = TableConfigurationModel.query.all()
        config_list = [
            {
                'id': configuration.id,
                'name': configuration.name,
                'description': configuration.description,
                'file_id': configuration.file_id,
                'file_name': configuration.file_name,
                'columns': configuration.columns,
                'model_type': ModelTypeModel.query.get(configuration.model_type_id).type_name,
                'hyper_parameters': configuration.hyper_parameters,
                'created_date': configuration.created_date
            }
            for configuration in configurations
        ]
        return config_list

    # update configuration
    @staticmethod
    def editTableConfiguration(configuration):
        # get the instance
        config = TableConfigurationModel.query.get(configuration.id)

        # check the instance whether is existed
        if not config:
            return False
        try:
            config.name = configuration.name
            config.description = configuration.description
            config.file_id = configuration.file_id
            config.file_name = configuration.file_name
            config.columns = configuration.columns
            config.model_type_id = configuration.model_type_id
            if configuration.hyper_parameters == {}:
                model_type = ModelTypeModel.query.filter_by(id=configuration.model_type_id).first()
                configuration.hyper_parameters = model_type.hyper_parameters

            config.hyper_parameters = configuration.hyper_parameters

            # update the details
            db.session.commit()
            return True
        # handle error and exception and return false
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    # delete Table Configuration
    @staticmethod
    def deleteTableConfiguration(configuration):
        # get the instance
        config = TableConfigurationModel.query.get(configuration.id)

        # check the instance is existed
        if not config:
            return False

        # check the configuration is referenced by model
        if config.model:
            return False

        try:
            # delete instance
            db.session.delete(config)
            db.session.commit()
            return True
        # handle exception and error and return false
        except Exception as e:
            print(e)
            db.session.rollback()
            return False


