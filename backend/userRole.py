# user role class
class UserRole:
    def __init__(self, role, description, status='ACTIVE'):
        self.role = role
        self.description = description
        self.status = status