from typing import List, Dict, Optional

# Initial State Variables
selected_farm_uuid: Optional[str] = None
farms_list: List[Dict] = []
current_farm_data: Dict = {}

# Authentication State (mirrors what AuthManager might push)
authenticated: bool = False
user_email: str = ""
user_role: str = ""
message: str = ""
message_type: str = "info"