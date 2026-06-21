class User:

    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

    def is_admin(self):
        return self.role.value == "admin"

    def can_write(self):
        return self.role.value in ["admin", "agent"]

    def can_delete(self):
        return self.role.value == "admin"