from Kernel.models.user import User
from Kernel.models.role import Role

user = User(
    id=1,
    username="admin",
    full_name="System Administrator",
    role=Role.ADMIN,
    is_active=True
)

print(user)
print(user.is_admin())