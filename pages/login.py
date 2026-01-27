from taipy.gui import Gui, State, Markdown
from src.auth.manager import auth_manager

def login_scenario(state: State):
    """
    Handles the login submission.
    """
    try:
        user_info = auth_manager.login(state.email, state.password)
        state.authenticated = user_info['authenticated']
        state.user_email = user_info['email']
        state.user_role = user_info['role']
        state.message = f"Login successful for {state.user_email} with role {state.user_role}!"
        state.message_type = "success"
    except ValueError as e:
        state.authenticated = False
        state.message = str(e)
        state.message_type = "error"
    except Exception as e:
        state.authenticated = False
        state.message = f"An unexpected error occurred: {str(e)}"
        state.message_type = "error"

def logout_scenario(state: State):
    """
    Handles the logout action.
    """
    auth_manager.logout()
    state.authenticated = False
    state.user_email = ""
    state.user_role = ""
    state.message = "Logged out successfully."
    state.message_type = "info"

def on_init(state: State):
    """
    Initialize state variables on page load.
    """
    state.email = ""
    state.password = ""
    state.message = ""
    state.message_type = "info" # or success, error
    state.authenticated = auth_manager.is_authenticated()
    if state.authenticated:
        current_user = auth_manager.get_current_user()
        state.user_email = current_user.get('email', '')
        state.user_role = current_user.get('role', '')
    else:
        state.user_email = ""
        state.user_role = ""

login_page = Markdown("""
<|{on_init}|on_init|>

<|part|render={not authenticated}|
# Login

<|{message}|
<|indicator|type={message_type}|>
|>

Email: <|{email}|input|>
Password: <|{password}|input|password=True|>

<|Login|button|on_action={login_scenario}|>
|>

<|part|render={authenticated}|
# Welcome, <|{user_email}|text>!

Your role is: <|{user_role}|text>

<|{message}|
<|indicator|type={message_type}|>
|>

<|Logout|button|on_action={logout_scenario}|>
|>
""")
