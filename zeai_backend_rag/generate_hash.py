from app.auth import hash_password

password = input("Enter the admin password you want to set: ")
hashed = hash_password(password)
print("\nHashed password (copy this):")
print(hashed)