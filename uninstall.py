#!/usr/bin/env python3
"""
Face Folio - Uninstaller Entry Point
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Simple entry point that launches the uninstaller UI.
Used to create Uninstall.exe with PyInstaller.

Author: Jampani Komal
Version: 1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os

# Add installer directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'installer'))

from installer.uninstaller_ui import UninstallerApp

if __name__ == "__main__":
    app = UninstallerApp()
    app.mainloop()
