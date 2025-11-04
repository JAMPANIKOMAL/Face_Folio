#!/usr/bin/env python3
"""
Face Folio - Main Entry Point
"""

import sys
import os
from PIL import Image, ImageTk
import customtkinter as ctk

# Add src directory to Python path
# This allows us to import from 'src.ui' and 'src.core'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import the main App class from our ui module
    from ui.main_window import App
except ImportError as e:
    print(f"Error: Failed to import main_window.py.")
    print(f"Details: {e}")
    # Show a simple Tkinter error box if CTk fails to load
    root = ctk.CTk()
    root.withdraw()
    import tkinter as tk
    tk.messagebox.showerror("Import Error", f"Failed to import App from ui.main_window.\n\n{e}")
    sys.exit(1)


def resource_path(relative_path):
    """
    Get absolute path to resource.
    This works for both development (running from source)
    and for PyInstaller (running from a bundled .exe).
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Not running in a PyInstaller bundle, use normal path
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def main():
    """Main entry point for the application"""
    print("Face Folio v1.0 - Starting application...")

    try:
        # Initialize the App, passing the resource_path function
        app = App(resource_path_func=resource_path)

        # --- Set the window icon (copied from AI Corrector project) ---
        try:
            # We provide 'assets' folder path to the app
            # The app will handle loading its own icon
            icon_path = resource_path(os.path.join("assets", "app_logo.ico"))
            
            if os.path.exists(icon_path):
                print(f"Loading icon from: {icon_path}")
                app.iconbitmap(icon_path)
            else:
                print(f"Warning: app_logo.ico not found at {icon_path}.")
                # Fallback for .png if .ico fails (e.g., on Linux)
                png_path = resource_path(os.path.join("assets", "app_logo.png"))
                if os.path.exists(png_path):
                    print(f"Loading fallback icon from: {png_path}")
                    icon_image = ImageTk.PhotoImage(Image.open(png_path))
                    app.iconphoto(False, icon_image)
                else:
                    print("Warning: No app_logo.png or app_logo.ico found.")
                    
        except Exception as e:
            print(f"Error loading icon: {e}")

        # Start the application loop
        app.mainloop()

    except Exception as e:
        print(f"Fatal Error: Failed to start application.")
        print(f"Details: {e}")
        import tkinter as tk
        # Use a basic Tkinter messagebox for fatal errors
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Application Error", f"A fatal error occurred:\n\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()