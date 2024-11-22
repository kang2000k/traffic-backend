import bcrypt
import io
from flask import session
from backend.Model import SystemAdminModel, TokenModel, SCOPES, db
from backend import Model
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


# system admin class
class SystemAdmin:

    # Login method
    def login(self, username, password):
        isPasswordValid = False

        # Check the username
        user = SystemAdminModel.query.filter_by(username=username).first()

        if user:
            # Validate the password
            isPasswordValid = self.check_password(user.hashed_password, password)

        # Add session if the password is correct
        if isPasswordValid:
            session['username'] = user.username
            session['role'] = user.role.role
            session.permanent = True
        return isPasswordValid

    # Check password
    def check_password(self, stored_hashed_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hashed_password.encode('utf-8'))

    # access google drive api
    def get_access_credentials(self):
        try:
            # find the credentials file
            file_name = 'credentials.json'
            folder_id = '1jZ5OH8nsTO9JtB2PB87BbsX7-sBiNc1x'
            results = Model.drive_service.files().list(
                q=f"name='{file_name}' and '{folder_id}' in parents",
                spaces='drive',
                fields="files(id, name)"
            ).execute()
            files = results.get('files', [])
            # check the file whether is existed
            if files:
                file_id = files[0]['id']
                print(f"Found file: {files[0]['name']} with ID: {file_id}")

                # get the file content and download it
                request = Model.drive_service.files().get_media(fileId=file_id)
                file_stream = io.BytesIO()
                downloader = MediaIoBaseDownload(file_stream, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")
                # Seek to the start of the stream and load JSON content
                file_stream.seek(0)
                print("File content loaded successfully.")

                with open('credentials.json', 'wb') as credentials_file:
                    credentials_file.write(file_stream.read())
                    print("Credentials file created")

                # use credentials to get the drive access
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes=SCOPES,
                                                                 redirect_uri='http://127.0.0.1:5000/callbackG')
                auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true',
                                                     prompt='consent')
                return {'auth_url': auth_url, 'state': state, 'message': 'Please authenticate with Google'}
            else:
                print("Credentials file is not found.")
                return False
        # handle error and exception and return false
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
        except Exception as error:
            print(f"An error occurred: {error}")
            return False

    # renew the token
    def renew_credentials(self):
        try:
            # find the credentials file
            file_name = 'credentials.json'
            folder_id = '1jZ5OH8nsTO9JtB2PB87BbsX7-sBiNc1x'
            results = Model.drive_service.files().list(
                q=f"name='{file_name}' and '{folder_id}' in parents",
                spaces='drive',
                fields="files(id, name)"
            ).execute()
            files = results.get('files', [])
            # check the credentials file whether is existed
            if files:
                file_id = files[0]['id']
                print(f"Found file: {files[0]['name']} with ID: {file_id}")

                # get the content and download to local
                request = Model.drive_service.files().get_media(fileId=file_id)
                file_stream = io.BytesIO()
                downloader = MediaIoBaseDownload(file_stream, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")
                # Seek to the start of the stream and load JSON content
                file_stream.seek(0)
                print("File content loaded successfully.")

                with open('credentials.json', 'wb') as credentials_file:
                    credentials_file.write(file_stream.read())
                    print("Credentials file created")

                # use credentials to get the drive access
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes=SCOPES,
                                                                 redirect_uri='http://127.0.0.1:5000/callbackR')
                auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true',
                    prompt='consent')
                return {'auth_url': auth_url, 'state': state, 'message': 'Please authenticate with Google'}
            else:
                print("Credentials file is not found.")
                return False
        # handle error and exception and return false
        except HttpError as error:
            print(f"An error occurred: {error}")
            if os.path.exists("credentials.json"):
                os.remove("credentials.json")
                print("Credentials file removed")
            return False
        except Exception as error:
            print(f"An error occurred: {error}")
            if os.path.exists("credentials.json"):
                os.remove("credentials.json")
                print("Credentials file removed")
            return False



