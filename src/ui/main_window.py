#!/usr/bin/env python3
"""
Face Folio - Main Application Window (UI)
"""

import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from PIL import Image

# --- THEME DEFINITIONS (Matching AI Corrector) ---
DARK_THEME = {
    "BG_COLOR": "#000000",
    "MENU_COLOR": "#1C1C1C",
    "ENTRY_COLOR": "#1C1C1C",
    "TEXT_COLOR": "#FFFFFF",
    "BTN_COLOR": "#FFFFFF",
    "BTN_TEXT_COLOR": "#000000",
    "BTN_HOVER_COLOR": "#E0E0E0",
    "DISABLED_COLOR": "#555555",
    "BORDER_COLOR": "#FFFFFF",
    "PROGRESS_COLOR": "#FFFFFF",
}

LIGHT_THEME = {
    "BG_COLOR": "#EAEAEA",
    "MENU_COLOR": "#F5F5F5",
    "ENTRY_COLOR": "#FFFFFF",
    "TEXT_COLOR": "#000000",
    "BTN_COLOR": "#000000",
    "BTN_TEXT_COLOR": "#FFFFFF",
    "BTN_HOVER_COLOR": "#333333",
    "DISABLED_COLOR": "#AAAAAA",
    "BORDER_COLOR": "#000000",
    "PROGRESS_COLOR": "#000000",
}

class App(ctk.CTk):
    """
    Main application window for Face Folio.
    """
    def __init__(self, resource_path_func=lambda p: p):
        super().__init__()

        self.resource_path = resource_path_func
        self.current_theme_name = ctk.get_appearance_mode()
        self.current_theme = DARK_THEME if self.current_theme_name == "Dark" else LIGHT_THEME

        # --- Window Configuration ---
        self.title("Face Folio - Photo Organizer")
        self.geometry("800x600")
        self.minsize(600, 450)
        self.configure(fg_color=self.current_theme["BG_COLOR"])

        # --- Main Layout ---
        # 1st row (title) is fixed height
        # 2nd row (main content) expands
        self.grid_rowconfigure(1, weight=1)
        # 1st column (sidebar) will be fixed width
        # 2nd column (main frame) expands
        self.grid_columnconfigure(1, weight=1)

        # --- Title Label ---
        self.title_label = ctk.CTkLabel(
            self,
            text="Face Folio",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        # Span across both columns
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        # --- Placeholder Frame ---
        # This frame will hold the main content
        self.main_frame = ctk.CTkFrame(self, fg_color=self.current_theme["BG_COLOR"])
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        
        self.placeholder_label = ctk.CTkLabel(
            self.main_frame,
            text="Main Application UI Will Go Here",
            font=ctk.CTkFont(size=18),
            text_color=self.current_theme["DISABLED_COLOR"]
        )
        self.placeholder_label.pack(expand=True, padx=20, pady=20)

        # --- Bind theme change ---
        # This will call check_theme_change whenever the window configuration changes
        # which includes system theme changes.
        self_check_theme_change_id = None
        def check_theme_change_debounced(event=None):
            nonlocal self_check_theme_change_id
            if self_check_theme_change_id:
                self.after_cancel(self_check_theme_change_id)
            self_check_theme_change_id = self.after(100, self.check_theme_change)

        self.bind("<Configure>", check_theme_change_debounced)
        print("Application initialized. Waiting for theme check...")
        self.after(200, self.check_theme_change) # Initial check

    def check_theme_change(self):
        """Detects if the system theme has changed and updates the UI."""
        try:
            new_theme_name = ctk.get_appearance_mode()
            if new_theme_name != self.current_theme_name:
                print(f"Theme changed from {self.current_theme_name} to {new_theme_name}")
                self.current_theme_name = new_theme_name
                self.current_theme = DARK_THEME if new_theme_name == "Dark" else LIGHT_THEME
                self.update_ui_theme()
        except Exception as e:
            print(f"Error in check_theme_change: {e}")

    def update_ui_theme(self):
        """Redraws the UI elements with the new theme colors."""
        print("Updating UI theme...")
        self.configure(fg_color=self.current_theme["BG_COLOR"])
        self.title_label.configure(text_color=self.current_theme["TEXT_COLOR"])
        self.main_frame.configure(fg_color=self.current_theme["BG_COLOR"])
        self.placeholder_label.configure(text_color=self.current_theme["DISABLED_COLOR"])
        
        # --- TODO: Update all other UI elements ---
        # (We will add more elements later)


if __name__ == "__main__":
    # This allows us to run main_window.py directly for testing
    print("Running main_window.py directly for testing...")
    
    # A simple resource_path function for testing
    # It assumes main_window.py is in src/ui/
    def test_resource_path(relative_path):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_path, relative_path)

    app = App(resource_path_func=test_resource_path)
    
    # Try to load icon for testing
    try:
        icon_path = test_resource_path(os.path.join("assets", "app_logo.ico"))
        if os.path.exists(icon_path):
            app.iconbitmap(icon_path)
        else:
            print(f"Test icon not found at: {icon_path}")
    except Exception as e:
        print(f"Error loading test icon: {e}")
        
    app.mainloop()