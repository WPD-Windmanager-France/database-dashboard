"""
WNDMNGR - Main entry point for cloud deployment (Render, etc.)
"""
import os
# Import EVERYTHING from app (variables, functions, page)
from app import *
from taipy.gui import Gui

# Create the GUI instance
gui = Gui(page=page)

# Get port from environment variable (Render sets this)
port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    # Run the app - production settings
    gui.run(
        host="0.0.0.0",
        port=port,
        title="WNDMNGR",
        dark_mode=False,
        debug=False,
        use_reloader=False
    )
