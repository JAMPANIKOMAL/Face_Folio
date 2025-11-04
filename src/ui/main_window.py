#!/usr/bin/env python3
"""
Face Folio - Main Application Window (UI)
"""

import customtkinter as ctk
import os
import threading
from tkinter import filedialog, messagebox
from PIL import Image

# --- NEW IMPORTS ---
# We will import these in the next step, but add them now
# from core.photo_organizer import find_images, sort_photos_into_folders
# from core.face_recognition import learn_known_faces, match_faces_in_photos
# --- END NEW IMPORTS ---


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

        # --- State Variables ---
        self.reference_folder = ctk.StringVar() # <-- NEW
        self.event_folder = ctk.StringVar()     # <-- RENAMED (was input_folder)
        self.output_folder = ctk.StringVar()
        self.is_processing = False

        # --- Window Configuration ---
        self.title("Face Folio - Photo Organizer")
        self.geometry("800x500") # Adjusted height for new button
        self.minsize(600, 450)
        self.configure(fg_color=self.current_theme["BG_COLOR"])

        # --- Main Layout ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title Label ---
        self.title_label = ctk.CTkLabel(
            self,
            text="Face Folio",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # --- Main Frame (for inputs and button) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # --- vvv NEW: Reference Folder vvv ---
        self.ref_label = ctk.CTkLabel(
            self.main_frame,
            text="1. Select Reference Folder:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.ref_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=10)

        self.ref_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.reference_folder,
            state="disabled",
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.ref_entry.grid(row=0, column=1, sticky="ew", pady=10)

        self.ref_btn = ctk.CTkButton(
            self.main_frame,
            text="Browse...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_reference_folder, # <-- NEW function
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        self.ref_btn.grid(row=0, column=2, sticky="e", padx=(10, 0), pady=10)
        # --- ^^^ END NEW ^^^ ---

        # --- Event Folder (was Input Folder) ---
        self.event_label = ctk.CTkLabel(
            self.main_frame,
            text="2. Select Event Folder:", # <-- RENAMED
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.event_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=10) # <-- Row 1

        self.event_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.event_folder, # <-- RENAMED
            state="disabled",
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.event_entry.grid(row=1, column=1, sticky="ew", pady=10) # <-- Row 1

        self.event_btn = ctk.CTkButton(
            self.main_frame,
            text="Browse...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_event_folder, # <-- RENAMED
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        self.event_btn.grid(row=1, column=2, sticky="e", padx=(10, 0), pady=10) # <-- Row 1

        # --- Output Folder ---
        self.output_label = ctk.CTkLabel(
            self.main_frame,
            text="3. Select Output Folder:", # <-- RENAMED
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.output_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=10) # <-- Row 2

        self.output_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.output_folder,
            state="disabled",
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.output_entry.grid(row=2, column=1, sticky="ew", pady=10) # <-- Row 2

        self.output_btn = ctk.CTkButton(
            self.main_frame,
            text="Browse...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_output_folder,
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        self.output_btn.grid(row=2, column=2, sticky="e", padx=(10, 0), pady=10) # <-- Row 2

        # --- Start Button ---
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
        self.start_btn.grid(row=3, column=0, columnspan=3, sticky="ew", padx=0, pady=(20, 0)) # <-- Row 3

        # --- Status Frame (at bottom) ---
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20)) # <-- Row 2
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready. Select all three folders to begin.",
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

        # --- Bind theme change ---
        self_check_theme_change_id = None
        def check_theme_change_debounced(event=None):
            nonlocal self_check_theme_change_id
            if self_check_theme_change_id:
                self.after_cancel(self_check_theme_change_id)
            self_check_theme_change_id = self.after(100, self.check_theme_change)
        self.bind("<Configure>", check_theme_change_debounced)
        self.after(200, self.check_theme_change)

        # --- Bind window close ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- vvv NEW/RENAMED FUNCTIONS vvv ---
    def select_reference_folder(self):
        """Open dialog to select the reference (known faces) folder."""
        folder_path = filedialog.askdirectory(title="Select Reference Folder (Known People)")
        if folder_path:
            self.reference_folder.set(folder_path)

    def select_event_folder(self):
        """Open dialog to select the source event photo folder."""
        folder_path = filedialog.askdirectory(title="Select Event Photo Folder (All Photos)")
        if folder_path:
            self.event_folder.set(folder_path)
    # --- ^^^ END NEW/RENAMED ^^^ ---

    def select_output_folder(self):
        """Open dialog to select the destination folder."""
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_folder.set(folder_path)

    def start_processing_thread(self):
        """
        Starts the photo processing in a separate thread
        to prevent the UI from freezing.
        """
        if self.is_processing:
            print("Already processing.")
            return

        # --- vvv VALIDATION LOGIC UPDATED vvv ---
        ref_folder = self.reference_folder.get()
        event_folder = self.event_folder.get()
        out_folder = self.output_folder.get()

        if not ref_folder or not os.path.isdir(ref_folder):
            messagebox.showerror("Error", "Please select a valid Reference folder.")
            return
        if not event_folder or not os.path.isdir(event_folder):
            messagebox.showerror("Error", "Please select a valid Event folder.")
            return
        if not out_folder or not os.path.isdir(out_folder):
            messagebox.showerror("Error", "Please select a valid Output folder.")
            return
        
        if ref_folder == event_folder or ref_folder == out_folder or event_folder == out_folder:
            messagebox.showwarning("Warning", "All three folders must be different.")
            return
        # --- ^^^ END VALIDATION ^^^ ---

        # Disable UI elements
        self.set_ui_processing_state(True)
        
        # Start the actual work in a new thread
        process_thread = threading.Thread(
            target=self.start_processing, 
            args=(ref_folder, event_folder, out_folder), # <-- Pass all 3 paths
            daemon=True
        )
        process_thread.start()


    # vvv --- THIS FUNCTION IS THE MAIN CHANGE --- vvv
    def start_processing(self, ref_folder, event_folder, out_folder):
        """
        THE CORE LOGIC.
        This runs in a separate thread.
        We are now calling our core DIP functions.
        """
        print(f"Processing started: {ref_folder}, {event_folder} -> {out_folder}")
        
        try:
            # --- We will build these functions in the next step ---
            # from core.face_recognition import learn_known_faces, match_faces_in_photos
            # from core.photo_organizer import find_images, sort_photos_into_folders

            # --- Step 1: Learn Known Faces ---
            self.update_status("Step 1/4: Learning faces from Reference folder...", 0.0)
            # known_faces_dict = learn_known_faces(ref_folder)
            print("SIM: Learning known faces...")
            import time; time.sleep(1) # Simulation
            # if not known_faces_dict:
            #     raise Exception("No faces found in reference folder.")
            
            # --- Step 2: Find all event photos ---
            self.update_status("Step 2/4: Finding all photos in Event folder...", 0.25)
            # event_image_paths = find_images(event_folder)
            print("SIM: Finding event photos...")
            time.sleep(1) # Simulation
            # if not event_image_paths:
            #     raise Exception("No images found in event folder.")

            # --- Step 3: Match faces in event photos ---
            self.update_status("Step 3/4: Matching faces in event photos...", 0.5)
            # This is the slowest step and will need to report progress
            # photo_to_people_map = match_faces_in_photos(event_image_paths, known_faces_dict, self.update_status)
            print("SIM: Matching faces...")
            time.sleep(2) # Simulation
            
            # --- Step 4: Sort photos ---
            self.update_status("Step 4/4: Sorting photos into output folders...", 0.9)
            # sort_photos_into_folders(photo_to_people_map, out_folder)
            print("SIM: Sorting photos...")
            time.sleep(1) # Simulation
            
            self.update_status("Processing complete! (Simulation)", 1.0)
            self.after(100, lambda: messagebox.showinfo("Complete", "Photo sorting finished successfully! (Simulation)"))
            
        except Exception as e:
            print(f"Error during processing: {e}")
            self.update_status(f"Error: {e}", 0)
            self.after(100, lambda: messagebox.showerror("Error", f"An error occurred during processing:\n\n{e}"))
            
        finally:
            # Re-enable UI elements
            self.set_ui_processing_state(False)
    # ^^^ --- THIS FUNCTION IS THE MAIN CHANGE --- ^^^


    def update_status(self, message, progress):
        """
        Updates the status label and progress bar.
        Must be called from the main thread using 'after'.
        """
        def _update():
            # Update status label
            self.status_label.configure(text=message)
            if "Error" in message:
                self.status_label.configure(text_color="red") # Or some theme color
            else:
                self.status_label.configure(text_color=self.current_theme["TEXT_COLOR"])
            
            # Update progress bar
            self.progress_bar.set(progress)
        
        self.after(0, _update)

    def set_ui_processing_state(self, is_processing):
        """Disables or enables UI elements during processing."""
        self.is_processing = is_processing
        state = "disabled" if is_processing else "normal"
        
        def _update_ui():
            # Update all 3 buttons
            self.ref_btn.configure(state=state)
            self.event_btn.configure(state=state)
            self.output_btn.configure(state=state)
            self.start_btn.configure(state=state)
            
            if is_processing:
                self.start_btn.configure(text="Processing...")
            else:
                self.start_btn.configure(text="Start Sorting Photos")
                self.status_label.configure(text="Ready.", text_color=self.current_theme["DISABLED_COLOR"])
                self.progress_bar.set(0)

        self.after(0, _update_ui)

    def on_closing(self):
        """Called when the user tries to close the window."""
        if self.is_processing:
            if messagebox.askyesno("Confirm", "Processing is in progress. Are you sure you want to exit?"):
                self.destroy()
        else:
            self.destroy()

    def check_theme_change(self, event=None):
        """Detects if the system theme has changed and updates the UI."""
        try:
            new_theme_name = ctk.get_appearance_mode()
            if new_theme_name != self.current_theme_name:
                self.current_theme_name = new_theme_name
                self.current_theme = DARK_THEME if new_theme_name == "Dark" else LIGHT_THEME
                self.update_ui_theme()
        except Exception as e:
            pass

    def update_ui_theme(self):
        """RedGrams the UI elements with the new theme colors."""
        self.configure(fg_color=self.current_theme["BG_COLOR"])
        self.title_label.configure(text_color=self.current_theme["TEXT_COLOR"])

        # Update all 3 sections
        self.ref_label.configure(text_color=self.current_theme["TEXT_COLOR"])
        self.ref_entry.configure(
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"]
        )
        self.ref_btn.configure(
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        
        self.event_label.configure(text_color=self.current_theme["TEXT_COLOR"])
        self.event_entry.configure(
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"]
        )
        self.event_btn.configure(
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        
        self.output_label.configure(text_color=self.current_theme["TEXT_COLOR"])
        self.output_entry.configure(
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"]
        )
        self.output_btn.configure(
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        
        self.start_btn.configure(
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        
        status_text_color = self.current_theme["DISABLED_COLOR"]
        if self.is_processing:
            status_text_color = self.current_theme["TEXT_COLOR"]
        self.status_label.configure(text_color=status_text_color)

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