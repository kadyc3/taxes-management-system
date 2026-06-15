from kernell.models.user import User
from kernell.models.role import Role

user = User(
    id=1,
    username="admin",
    full_name="System Administrator",
    role=Role.ADMIN,
    is_active=True
)

print(user)
print(user.is_admin())