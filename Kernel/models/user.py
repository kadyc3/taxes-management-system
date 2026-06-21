class User:
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

    def is_admin(self):
        return self.role.value.lower() == "admin"

    def can_write(self):
        return self.role.value.lower() in ["admin", "editor"]

    def can_delete(self):
        return self.role.value.lower() == "admin"