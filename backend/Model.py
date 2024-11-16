from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table
import os

# database configuration
db = SQLAlchemy()
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://u7a3pa6u8gaec1:p0b7b9433ab6dc153fc19867c01df5de8438efaef5d70ef2a5b12963053d22bea@c724r43q8jp5nk.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/daba87psraiu08')

# create engine and metadata for reflection
engine = create_engine(SQLALCHEMY_DATABASE_URI)
metadata = MetaData()
metadata.reflect(bind=engine)

# google drive api configuration
SCOPES = [os.getenv('drive_scope', "https://www.googleapis.com/auth/drive")]
drive_service = None
sys_service = None

# thread pool and process pool executor configuration
executor = None
process_executor = None
thread_worker_count = 6
process_worker_count = 3
current_thread_worker_count = 0

# reflect the tables
UserRole = Table('userrole', metadata, autoload_with=engine)
UserAccount = Table('useraccount', metadata, autoload_with=engine)
SystemAdmin = Table('systemadmin', metadata, autoload_with=engine)
PullingConfig = Table('pullingconfiguration', metadata, autoload_with=engine)
ModelType = Table('modeltype', metadata, autoload_with=engine)
TableConfiguration = Table('tableconfiguration', metadata, autoload_with=engine)
ModelTrained = Table('model', metadata, autoload_with=engine)
Task = Table('task', metadata, autoload_with=engine)
Token = Table('token', metadata, autoload_with=engine)


# define models
class UserRoleModel(db.Model):
    __table__ = UserRole
    users = db.relationship('UserAccountModel', backref='role', lazy=True)
    system_admins = db.relationship('SystemAdminModel', backref='role', lazy=True)


class UserAccountModel(db.Model):
    __table__ = UserAccount


class SystemAdminModel(db.Model):
    __table__ = SystemAdmin


class PullingConfigurationModel(db.Model):
    __table__ = PullingConfig


class ModelTypeModel(db.Model):
    __table__ = ModelType
    table_configs = db.relationship('TableConfigurationModel', backref='model_type', lazy=True)


class TableConfigurationModel(db.Model):
    __table__ = TableConfiguration
    model = db.relationship('ModelTrainedModel', backref='table_configuration', lazy=True)


class ModelTrainedModel(db.Model):
    __table__ = ModelTrained
    tasks = db.relationship('TaskModel', backref='model_trained', lazy=True)


class TaskModel(db.Model):
    __table__ = Task


class TokenModel(db.Model):
    __table__ = Token