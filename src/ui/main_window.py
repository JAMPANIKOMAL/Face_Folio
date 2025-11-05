#!/usr/bin/env python3
"""
Face Folio - Main Application Window (UI)
"""

import customtkinter as ctk
import os
import threading
from tkinter import filedialog, messagebox
from PIL import Image
from pathlib import Path
import time

# ---
# --- (NO CHANGE FROM PREVIOUS STEP) ---
# ---
from core.photo_organizer import run_reference_sort
# --- END IMPORTS ---


# --- THEME DEFINITIONS (NO CHANGE) ---
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

        # --- State Variables (NO CHANGE) ---
        self.reference_folder = ctk.StringVar()
        self.event_folder = ctk.StringVar()
        self.output_folder = ctk.StringVar()
        self.is_processing = False
        self.valid_extensions = VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.zip')

        # --- Window Configuration (NO CHANGE) ---
        self.title("Face Folio - Photo Organizer")
        self.geometry("800x500") 
        self.minsize(600, 450)
        self.configure(fg_color=self.current_theme["BG_COLOR"])

        # --- Main Layout (NO CHANGE) ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title Label (NO CHANGE) ---
        self.title_label = ctk.CTkLabel(
            self,
            text="Face Folio",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # ---
        # --- FIX #3: RE-ORGANIZE THE LAYOUT FOR NEW BUTTONS ---
        # ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        # Configure column 1 (the entry box) to stretch
        self.main_frame.grid_columnconfigure(1, weight=1)
        # Add columns 2 and 3 for the new buttons
        self.main_frame.grid_columnconfigure(2, weight=0)
        self.main_frame.grid_columnconfigure(3, weight=0)


        # --- Reference Folder (Buttons changed) ---
        self.ref_label = ctk.CTkLabel(
            self.main_frame,
            text="1. Select Reference Input:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.ref_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=10)

        self.ref_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.reference_folder,
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.ref_entry.grid(row=0, column=1, sticky="ew", pady=10)

        # --- NEW "SELECT FILE" BUTTON ---
        self.ref_btn_file = ctk.CTkButton(
            self.main_frame,
            text="Select File/ZIP...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_reference_file, # New command
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            width=120
        )
        self.ref_btn_file.grid(row=0, column=2, sticky="e", padx=(10, 5), pady=10)

        # --- NEW "SELECT FOLDER" BUTTON ---
        self.ref_btn_folder = ctk.CTkButton(
            self.main_frame,
            text="Select Folder...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_reference_folder, # New command
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            width=120
        )
        self.ref_btn_folder.grid(row=0, column=3, sticky="e", padx=(0, 0), pady=10)


        # --- Event Folder (Buttons changed) ---
        self.event_label = ctk.CTkLabel(
            self.main_frame,
            text="2. Select Event Input:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.event_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=10)

        self.event_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.event_folder,
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.event_entry.grid(row=1, column=1, sticky="ew", pady=10)

        # --- NEW "SELECT FILE" BUTTON ---
        self.event_btn_file = ctk.CTkButton(
            self.main_frame,
            text="Select File/ZIP...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_event_file, # New command
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            width=120
        )
        self.event_btn_file.grid(row=1, column=2, sticky="e", padx=(10, 5), pady=10)

        # --- NEW "SELECT FOLDER" BUTTON ---
        self.event_btn_folder = ctk.CTkButton(
            self.main_frame,
            text="Select Folder...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_event_folder, # New command
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            width=120
        )
        self.event_btn_folder.grid(row=1, column=3, sticky="e", padx=(0, 0), pady=10)


        # --- Output Folder (Button layout updated) ---
        self.output_label = ctk.CTkLabel(
            self.main_frame,
            text="3. Select Output Folder:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.output_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=10)

        self.output_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.output_folder,
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.output_entry.grid(row=2, column=1, sticky="ew", pady=10)

        # --- UPDATED: Button now spans 2 columns to align ---
        self.output_btn = ctk.CTkButton(
            self.main_frame,
            text="Browse...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_output_folder, # This command was already fine
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        self.output_btn.grid(row=2, column=2, columnspan=2, sticky="ew", padx=(10, 0), pady=10)


        # --- Start Button (Columnspan updated) ---
        self.start_btn = ctk.CTkButton(
            self.main_frame,
            text="Start Sorting Photos",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_processing_thread,
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            height=40
        )
        # --- UPDATED: columnspan is now 4 ---
        self.start_btn.grid(row=3, column=0, columnspan=4, sticky="ew", padx=0, pady=(20, 0))

        # --- Status Frame (NO CHANGE) ---
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready. Select all three inputs to begin.",
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme["DISABLED_COLOR"]
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=0, pady=0)
        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame,
            progress_color=self.current_theme["PROGRESS_COLOR"],
            fg_color=self.current_theme["ENTRY_COLOR"],
            border_width=1,
            border_color=self.current_theme["BORDER_COLOR"]
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=0, pady=(5, 0))

        # --- Bind theme change (NO CHANGE) ---
        self_check_theme_change_id = None
        def check_theme_change_debounced(event=None):
            nonlocal self_check_theme_change_id
            if self_check_theme_change_id:
                self.after_cancel(self_check_theme_change_id)
            self_check_theme_change_id = self.after(100, self.check_theme_change)
        self.bind("<Configure>", check_theme_change_debounced)
        self.after(200, self.check_theme_change)

        # --- Bind window close (NO CHANGE) ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ---
    # --- FIX #3: REMOVED THE BAD LOGIC ---
    # ---
    #
    # The old, confusing '_get_input_path' function has been
    # REMOVED entirely.
    #
    # --- END REMOVAL ---
    
    # ---
    # --- FIX #3: ADDED NEW, CLEAR LOGIC ---
    # ---
    
    def _select_input_file(self, target_variable, title):
        """Helper to ask for a single File or ZIP."""
        options = {}
        if 'zip' in self.valid_extensions:
            options['filetypes'] = (("Image or Zip Files", "*.jpg *.jpeg *.png *.zip"), ("All files", "*.*"))
        else:
            options['filetypes'] = (("Image Files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
            
        path = filedialog.askopenfilename(title=title, **options)
        if path:
            target_variable.set(path)

    def _select_input_folder(self, target_variable, title):
        """Helper to ask for a Folder."""
        folder_path = filedialog.askdirectory(title=title)
        if folder_path:
            target_variable.set(folder_path)

    # --- New functions for the new buttons ---
    def select_reference_file(self):
        """Open dialog to select the reference (known faces) file/zip."""
        self._select_input_file(self.reference_folder, "Select Reference File/ZIP")

    def select_reference_folder(self):
        """Open dialog to select the reference (known faces) folder."""
        self._select_input_folder(self.reference_folder, "Select Reference Folder")

    def select_event_file(self):
        """Open dialog to select the source event photo file/zip."""
        self._select_input_file(self.event_folder, "Select Event File/ZIP")

    def select_event_folder(self):
        """Open dialog to select the source event photo folder."""
        self._select_input_folder(self.event_folder, "Select Event Folder")
        
    def select_output_folder(self):
        """Open dialog to select the destination folder. (No change)"""
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_folder.set(folder_path)

    # ---
    # --- END FIX #3 ---
    # ---

    def start_processing_thread(self):
        """
        Starts the photo processing in a separate thread.
        (No change to this function, it's just checking paths)
        """
        if self.is_processing:
            print("Already processing.")
            return

        ref_folder = self.reference_folder.get()
        event_folder = self.event_folder.get()
        out_folder = self.output_folder.get()

        if not ref_folder or not Path(ref_folder).exists():
            messagebox.showerror("Error", "Please select a valid Reference input (Folder/Image/ZIP).")
            return
        if not event_folder or not Path(event_folder).exists():
            messagebox.showerror("Error", "Please select a valid Event input (Folder/Image/ZIP).")
            return
        if not out_folder or not Path(out_folder).is_dir():
            messagebox.showerror("Error", "Please select a valid Output folder.")
            return
        
        if ref_folder == event_folder or ref_folder == out_folder or event_folder == out_folder:
            messagebox.showwarning("Warning", "All three paths must be unique.")
            return

        self.set_ui_processing_state(True)
        
        process_thread = threading.Thread(
            target=self.start_processing, 
            args=(ref_folder, event_folder, out_folder),
            daemon=True
        )
        process_thread.start()

    # ---
    # --- (NO CHANGE FROM PREVIOUS STEP) ---
    # ---
    def start_processing(self, ref_folder, event_folder, out_folder):
        """
        THE REAL CORE LOGIC.
        This runs in a separate thread and calls our core functions.
        """
        print(f"Processing started: {ref_folder}, {event_folder} -> {out_folder}")
        
        try:
            # This is still correctly calling our restored 'run_reference_sort'
            run_reference_sort(
                ref_folder,
                event_folder,
                out_folder,
                self.update_status # Pass the callback function
            )
            
            self.update_status("Processing complete!", 1.0)
            self.after(100, lambda: messagebox.showinfo("Complete", "Photo sorting finished successfully!"))
            
        except Exception as e:
            print(f"Error during processing: {e}")
            self.update_status(f"Error: {e}", 0)
            self.after(100, lambda: messagebox.showerror("Error", f"An error occurred during processing:\n\n{e}"))
            
        finally:
            # Re-enable UI elements
            self.set_ui_processing_state(False)

    def update_status(self, message, progress):
        """
        Updates the status label and progress bar. (No change)
        """
        def _update():
            # Update status label
            self.status_label.configure(text=message)
            if "Error" in message:
                self.status_label.configure(text_color="red")
            else:
                self.status_label.configure(text_color=self.current_theme["TEXT_COLOR"])
            
            # Update progress bar
            self.progress_bar.set(progress)
        
        self.after(0, _update)

    def set_ui_processing_state(self, is_processing):
        """Disables or enables UI elements during processing. (Button names updated)"""
        self.is_processing = is_processing
        state = "disabled" if is_processing else "normal"
        
        def _update_ui():
            # --- UPDATED: Disable all 4 new buttons ---
            self.ref_btn_file.configure(state=state)
            self.ref_btn_folder.configure(state=state)
            self.event_btn_file.configure(state=state)
            self.event_btn_folder.configure(state=state)
            self.output_btn.configure(state=state)
            self.start_btn.configure(state=state)
            
            self.progress_bar.set(0)

            if is_processing:
                self.start_btn.configure(text="Processing...")
                self.ref_entry.configure(state="disabled")
                self.event_entry.configure(state="disabled")
                self.output_entry.configure(state="disabled")
                self.status_label.configure(text="Processing started...", text_color=self.current_theme["TEXT_COLOR"])
            else:
                self.start_btn.configure(text="Start Sorting Photos")
                self.ref_entry.configure(state="normal")
                self.event_entry.configure(state="normal")
                self.output_entry.configure(state="normal")
                self.status_label.configure(text="Ready. Select all three inputs to begin.", text_color=self.current_theme["DISABLED_COLOR"])
                

        self.after(0, _update_ui)

    def on_closing(self):
        """Called when the user tries to close the window. (No change)"""
        if self.is_processing:
            if messagebox.askyesno("Confirm", "Processing is in progress. Are you sure you want to exit?"):
                self.destroy()
        else:
            self.destroy()

    def check_theme_change(self, event=None):
        """Detects if the system theme has changed and updates the UI. (No change)"""
        try:
            new_theme_name = ctk.get_appearance_mode()
            if new_theme_name != self.current_theme_name:
                self.current_theme_name = new_theme_name
                self.current_theme = DARK_THEME if new_theme_name == "Dark" else LIGHT_THEME
                self.update_ui_theme()
        except Exception as e:
            pass

    def update_ui_theme(self):
        """Redraws the UI elements with the new theme colors. (Button names updated)"""
        self.configure(fg_color=self.current_theme["BG_COLOR"])
        self.title_label.configure(text_color=self.current_theme["TEXT_COLOR"])

        elements_to_update = [self.ref_label, self.event_label, self.output_label, self.status_label]
        for elem in elements_to_update:
            elem.configure(text_color=self.current_theme["TEXT_COLOR"])

        for entry in [self.ref_entry, self.event_entry, self.output_entry]:
            entry.configure(
                fg_color=self.current_theme["ENTRY_COLOR"],
                text_color=self.current_theme["TEXT_COLOR"],
                border_color=self.current_theme["BORDER_COLOR"]
            )
            
        # --- UPDATED: Include all new buttons in theme change ---
        for btn in [self.ref_btn_file, self.ref_btn_folder, self.event_btn_file, Self.event_btn_folder, self.output_btn, self.start_btn]:
            btn.configure(
                fg_color=self.current_theme["BTN_COLOR"],
                text_color=self.current_theme["BTN_TEXT_COLOR"],
                hover_color=self.current_theme["BTN_HOVER_COLOR"]
            )

        self.progress_bar.configure(
            progress_color=self.current_theme["PROGRESS_COLOR"],
            fg_color=self.current_theme["ENTRY_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"]
        )


if __name__ == "__main__":
    # This allows us to run main_window.py directly for testing
    print("Running main_window.py directly for testing...")
    
    def test_resource_path(relative_path):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_path, relative_path)

    app = App(resource_path_func=test_resource_path)
    
    try:
        icon_path = test_resource_path(os.path.join("assets", "app_logo.ico"))
        if os.path.exists(icon_path):
            app.iconbitmap(icon_path)
        else:
            print(f"Test icon not found at: {icon_path}")
    except Exception as e:
        print(f"Error loading test icon: {e}")
        
    app.mainloop()