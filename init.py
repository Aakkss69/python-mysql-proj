import random
from database.role import RoleManager
from database.user import UserManager
from database.task import TaskManager

def initialize_database():
    # Initialize the database and ensure tables are created
    role_manager = RoleManager()
    user_manager = UserManager()
    task_manager = TaskManager()

    db = user_manager.db  # Use the existing database connection from UserManager
    db.connect()
    db.create_tables()

    # Ensure roles exist
    roles = role_manager.get_roles()
    role_names = [role[1] for role in roles]

    if "Admin" not in role_names:
        role_manager.add_role("Admin")
    if "User" not in role_names:
        role_manager.add_role("User")

    # Fetch roles to get the role IDs
    roles = role_manager.get_roles()

    # Temporary code to add admin_user
    admin_username = "admin_user"
    admin_password = "admin_pass"  # Use a secure password in a real application
    role_id = roles[0][0]  # Assuming 0 index is Admin role ID

    user_username = "amitesh"
    user_password = "amitesh"
    user_role_id = roles[1][0]  # Assuming 1 index is User role ID

    usernames = [user[1] for user in user_manager.get_users()]

    # Check if the admin_user already exists to avoid duplicates
    if admin_username not in usernames:
        user_manager.add_user(admin_username, admin_password, role_id)
        print(f"Admin user '{admin_username}' added successfully.")
    else:
        print(f"Admin user '{admin_username}' already exists.")

    # Check if amitesh already exists to avoid duplicates
    if user_username not in usernames:
        user_manager.add_user(user_username, user_password, user_role_id)
        print(f"Amitesh user '{user_username}' added successfully.")
    else:
        print(f"Amitesh user '{user_username}' already exists.")

    # Add random tasks for the users
    task_titles = [
        "Complete report", "Update website", "Analyze data", "Prepare presentation",
        "Attend meeting", "Review document", "Develop feature", "Test application",
        "Deploy system", "Optimize code"
    ]

    users = user_manager.get_users()
    for user in users:
        # Generate a random number of tasks for each user (e.g., between 1 and 5 tasks)
        num_tasks = random.randint(1, 5)
        existing_tasks = [task for task in task_manager.get_tasks() if task[4] == user[0]]
        if len(existing_tasks) < num_tasks:
            for j in range(num_tasks - len(existing_tasks)):
                task_title = random.choice(task_titles)
                task_description = f"{task_title} for {user[1]}"
                task_manager.add_task(task_title, task_description, "2024-12-31", user[0])

    # Clean up connections
    role_manager.close_connection()
    user_manager.close_connection()
    task_manager.close_connection()
