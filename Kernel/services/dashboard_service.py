class DashboardService:

    def __init__(self, user):
        self.user = user

    def get_dashboard_data(self):
        return {
            "username": self.user.username,
            "role": self.user.role.value,
        }