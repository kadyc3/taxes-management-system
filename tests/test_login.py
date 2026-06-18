from Infrastructure.repositories.user_repository import UserRepository
from Kernel.services.auth_service import AuthService

repo = UserRepository()
auth = AuthService(repo)

user = auth.login("admin", "admin123")

print(user)
print(user.username)
print(user.role)

