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
import subprocess # NEW IMPORT for opening the folder

# ---
# --- NEW: IMPORT BOTH CORE FUNCTIONS ---
# ---
# We now need both functions from our core logic file
#
from core.photo_organizer import run_reference_sort, run_auto_discovery
# --- END NEW IMPORTS ---


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

        # --- State Variables ---
        self.current_mode = ctk.StringVar(value="Reference Sort")
        self.reference_folder = ctk.StringVar()
        self.event_folder = ctk.StringVar()
        self.output_folder = ctk.StringVar()
        self.is_processing = False
        self.valid_extensions = VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.zip')

        # --- Window Configuration (NO CHANGE) ---
        self.title("Face Folio - Photo Organizer")
        self.geometry("800x550") # <-- Increased height slightly for new button
        self.minsize(600, 500)
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
        
        # --- Main Frame (for inputs) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=0)
        self.main_frame.grid_columnconfigure(3, weight=0)

        # ---
        # --- NEW: MODE SWITCHER ---
        # ---
        self.mode_switcher = ctk.CTkSegmentedButton(
            self.main_frame,
            values=["Reference Sort", "Auto-Discovery"],
            command=self.on_mode_change,
            variable=self.current_mode,
            font=ctk.CTkFont(size=14, weight="bold"),
            selected_color=self.current_theme["BTN_COLOR"],
            selected_hover_color=self.current_theme["BTN_HOVER_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            text_color_disabled=self.current_theme["DISABLED_COLOR"],
            unselected_color=self.current_theme["ENTRY_COLOR"],
            unselected_hover_color=self.current_theme["MENU_COLOR"],
            fg_color=self.current_theme["ENTRY_COLOR"]
        )
        self.mode_switcher.grid(row=0, column=0, columnspan=4, sticky="ew", padx=0, pady=(0, 15))
        # --- END NEW FEATURE ---


        # --- Reference Folder (Row index changed) ---
        # We need to store these widgets so we can hide/show them
        self.ref_label = ctk.CTkLabel(
            self.main_frame,
            text="1. Select Reference Input:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.ref_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=10) # <-- row=1

        self.ref_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.reference_folder,
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.ref_entry.grid(row=1, column=1, sticky="ew", pady=10) # <-- row=1

        self.ref_btn_file = ctk.CTkButton(
            self.main_frame,
            text="Select File/ZIP...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_reference_file, 
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            width=120
        )
        self.ref_btn_file.grid(row=1, column=2, sticky="e", padx=(10, 5), pady=10) # <-- row=1

        self.ref_btn_folder = ctk.CTkButton(
            self.main_frame,
            text="Select Folder...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_reference_folder, 
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            width=120
        )
        self.ref_btn_folder.grid(row=1, column=3, sticky="e", padx=(0, 0), pady=10) # <-- row=1

        # Store all reference widgets in a list for easy hiding/showing
        self.reference_widgets = [self.ref_label, self.ref_entry, self.ref_btn_file, self.ref_btn_folder]


        # --- Event Folder (Row index changed) ---
        self.event_label = ctk.CTkLabel(
            self.main_frame,
            text="2. Select Event Input:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.event_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=10) # <-- row=2

        self.event_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.event_folder,
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.event_entry.grid(row=2, column=1, sticky="ew", pady=10) # <-- row=2

        self.event_btn_file = ctk.CTkButton(
            self.main_frame,
            text="Select File/ZIP...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_event_file,
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            width=120
        )
        self.event_btn_file.grid(row=2, column=2, sticky="e", padx=(10, 5), pady=10) # <-- row=2

        self.event_btn_folder = ctk.CTkButton(
            self.main_frame,
            text="Select Folder...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_event_folder, 
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            width=120
        )
        self.event_btn_folder.grid(row=2, column=3, sticky="e", padx=(0, 0), pady=10) # <-- row=2


        # --- Output Folder (Row index changed) ---
        self.output_label = ctk.CTkLabel(
            self.main_frame,
            text="3. Select Output Folder:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.current_theme["TEXT_COLOR"]
        )
        self.output_label.grid(row=3, column=0, sticky="w", padx=(0, 10), pady=10) # <-- row=3

        self.output_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.output_folder,
            font=ctk.CTkFont(size=12),
            fg_color=self.current_theme["ENTRY_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"],
            border_width=1
        )
        self.output_entry.grid(row=3, column=1, sticky="ew", pady=10) # <-- row=3

        self.output_btn = ctk.CTkButton(
            self.main_frame,
            text="Select Folder...",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.select_output_folder,
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"]
        )
        self.output_btn.grid(row=3, column=2, columnspan=2, sticky="ew", padx=(10, 0), pady=10) # <-- row=3

        
        # --- Status Frame (at bottom) (NO CHANGE) ---
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.start_btn = ctk.CTkButton(
            self.status_frame, 
            text="Start Sorting Photos",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_processing_thread,
            fg_color=self.current_theme["BTN_COLOR"],
            text_color=self.current_theme["BTN_TEXT_COLOR"],
            hover_color=self.current_theme["BTN_HOVER_COLOR"],
            height=40
        )
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 15))


        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready. Select inputs to begin.",
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme["DISABLED_COLOR"]
        )
        self.status_label.grid(row=1, column=0, sticky="w", padx=0, pady=0)

        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame,
            progress_color=self.current_theme["PROGRESS_COLOR"],
            fg_color=self.current_theme["ENTRY_COLOR"],
            border_width=1,
            border_color=self.current_theme["BORDER_COLOR"]
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=0, pady=(5, 0))

        # --- Bind theme change ---
        self_check_theme_change_id = None
        def check_theme_change_debounced(event=None):
            nonlocal self_check_theme_change_id
            if self_check_theme_change_id:
                self.after_cancel(self_check_theme_change_id)
            self_check_theme_change_id = self.after(100, self.check_theme_change)
        self.bind("<Configure>", check_theme_change_debounced)
        self.after(200, self.check_theme_change)
        self.after(250, lambda: self.on_mode_change(self.current_mode.get())) # Set initial state

        # --- Bind window close (NO CHANGE) ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ---
    # --- NEW: HIDE/SHOW LOGIC ---
    # ---
    def on_mode_change(self, mode):
        """Called by the segmented button to hide/show the reference row."""
        if mode == "Reference Sort":
            for widget in self.reference_widgets:
                widget.grid() # Show widgets
            self.ref_label.configure(text="1. Select Reference Input:")
            self.event_label.configure(text="2. Select Event Input:")
            self.output_label.configure(text="3. Select Output Folder:")
            self.start_btn.configure(text="Start Sorting Photos")
        
        elif mode == "Auto-Discovery":
            for widget in self.reference_widgets:
                widget.grid_remove() # Hide widgets
            self.ref_label.configure(text="") # Clear text to prevent layout shift
            self.event_label.configure(text="1. Select Event Input:")
            self.output_label.configure(text="2. Select Output Folder:")
            self.start_btn.configure(text="Start Auto-Discovery")
    # --- END NEW FEATURE ---

    # --- Button Command Functions (NO CHANGE) ---
    
    def _select_input_file(self, target_variable, title):
        options = {}
        if 'zip' in self.valid_extensions:
            options['filetypes'] = (("Image or Zip Files", "*.jpg *.jpeg *.png *.zip"), ("All files","*.*"))
        else:
            options['filetypes'] = (("Image Files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
            
        path = filedialog.askopenfilename(title=title, **options)
        if path:
            target_variable.set(path)

    def _select_input_folder(self, target_variable, title):
        folder_path = filedialog.askdirectory(title=title)
        if folder_path:
            target_variable.set(folder_path)

    def select_reference_file(self):
        self._select_input_file(self.reference_folder, "Select Reference File/ZIP")

    def select_reference_folder(self):
        self._select_input_folder(self.reference_folder, "Select Reference Folder")

    def select_event_file(self):
        self._select_input_file(self.event_folder, "Select Event File/ZIP")

    def select_event_folder(self):
        self._select_input_folder(self.event_folder, "Select Event Folder")
        
    def select_output_folder(self):
        self._select_input_folder(self.output_folder, "Select Output Folder")


    # ---
    # --- UPDATED: PROCESSING LOGIC ---
    # ---
    def start_processing_thread(self):
        """
        Starts the photo processing in a separate thread.
        Now checks which mode is active.
        """
        if self.is_processing:
            print("Already processing.")
            return

        mode = self.current_mode.get()
        event_folder = self.event_folder.get()
        out_folder = self.output_folder.get()

        # --- Validation for BOTH modes ---
        if not event_folder or not Path(event_folder).exists():
            messagebox.showerror("Error", "Please select a valid Event input (Folder/Image/ZIP).")
            return
        if not out_folder or not Path(out_folder).is_dir():
            messagebox.showerror("Error", "Please select a valid Output folder.")
            return
        
        if mode == "Reference Sort":
            ref_folder = self.reference_folder.get()
            if not ref_folder or not Path(ref_folder).exists():
                messagebox.showerror("Error", "Please select a valid Reference input (Folder/Image/ZIP).")
                return
            if ref_folder == event_folder or ref_folder == out_folder:
                messagebox.showwarning("Warning", "All three paths must be unique.")
                return
        
        if event_folder == out_folder:
            messagebox.showwarning("Warning", "Event and Output paths must be unique.")
            return

        self.set_ui_processing_state(True)
        
        # --- NEW: Call the correct thread target based on mode ---
        if mode == "Reference Sort":
            process_thread = threading.Thread(
                target=self.run_reference_sort_process, 
                args=(self.reference_folder.get(), event_folder, out_folder),
                daemon=True
            )
        else: # Auto-Discovery
            process_thread = threading.Thread(
                target=self.run_auto_discovery_process, 
                args=(event_folder, out_folder),
                daemon=True
            )
            
        process_thread.start()

    def run_reference_sort_process(self, ref_folder, event_folder, out_folder):
        """The processing logic for Reference Sort mode."""
        print(f"Processing (Reference Sort) started: {ref_folder}, {event_folder} -> {out_folder}")
        
        try:
            run_reference_sort(
                ref_folder,
                event_folder,
                out_folder,
                self.update_status 
            )
            
            self.update_status("Processing complete!", 1.0)
            self.after(100, lambda: messagebox.showinfo("Complete", "Photo sorting finished successfully!"))
            
        except Exception as e:
            print(f"Error during processing: {e}")
            self.update_status(f"Error: {e}", 0)
            self.after(100, lambda: messagebox.showerror("Error", f"An error occurred during processing:\n\n{e}"))
            
        finally:
            self.set_ui_processing_state(False)

    def run_auto_discovery_process(self, event_folder, out_folder):
        """The new, multi-step processing logic for Auto-Discovery mode."""
        print(f"Processing (Auto-Discovery) started: {event_folder} -> {out_folder}")
        
        try:
            # --- Step 1: Find unique faces ---
            self.update_status("Step 1/3: Finding unique faces...", 0.1)
            portraits_dir = os.path.join(out_folder, "_Portraits_To_Tag")
            
            portrait_files = run_auto_discovery(
                event_folder,
                out_folder,
                self.update_status
            )
            
            if not portrait_files:
                self.update_status("No faces were found in the event photos.", 0)
                self.after(100, lambda: messagebox.showwarning("No Faces Found", "No faces were detected in any of the event photos."))
                self.set_ui_processing_state(False)
                return

            self.update_status("Step 2/3: Waiting for user to tag portraits...", 0.6)
            
            # --- Step 2: Stop and ask user to tag ---
            # We must run this on the main thread using .after()
            def ask_user_to_tag():
                try:
                    # Open the folder for the user
                    if os.name == 'nt': # Windows
                        os.startfile(portraits_dir)
                    elif os.name == 'posix': # macOS/Linux
                        subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', portraits_dir))
                except Exception as e:
                    print(f"Could not auto-open folder: {e}")

                # Show the blocking message box
                messagebox.showinfo(
                    "Tag Your Photos",
                    f"I found {len(portrait_files)} unique people!\n\n"
                    f"I have opened the folder:\n{portraits_dir}\n\n"
                    "Please rename the 'Person_X.jpg' files to their real names (e.g., 'Alice.jpg').\n\n"
                    "Click OK when you are finished."
                )
                
                # --- Step 3: Start the final sort (after user clicks OK) ---
                self.update_status("Step 3/3: Sorting photos based on tags...", 0.7)
                
                # We need a new thread for this final step
                final_sort_thread = threading.Thread(
                    target=self.run_final_sort_process,
                    args=(portraits_dir, event_folder, out_folder),
                    daemon=True
                )
                final_sort_thread.start()

            self.after(100, ask_user_to_tag)

        except Exception as e:
            print(f"Error during auto-discovery: {e}")
            self.update_status(f"Error: {e}", 0)
            self.after(100, lambda: messagebox.showerror("Error", f"An error occurred during discovery:\n\n{e}"))
            self.set_ui_processing_state(False)

    def run_final_sort_process(self, portraits_dir, event_folder, out_folder):
        """This is the final step, called after the user tags the files."""
        try:
            # We just re-use the reference sort, pointing it at the new portraits dir!
            run_reference_sort(
                portraits_dir,
                event_folder,
                out_folder,
                lambda msg, prog: self.update_status(f"Step 3/3: {msg}", 0.7 + (prog * 0.3))
            )
            
            self.update_status("Auto-Discovery complete!", 1.0)
            self.after(100, lambda: messagebox.showinfo("Complete", "Photo sorting finished successfully!"))

        except Exception as e:
            print(f"Error during final sort: {e}")
            self.update_status(f"Error: {e}", 0)
            self.after(100, lambda: messagebox.showerror("Error", f"An error occurred during the final sort:\n\n{e}"))
            
        finally:
            self.set_ui_processing_state(False)
    # --- END UPDATED LOGIC ---


    def update_status(self, message, progress):
        def _update():
            self.status_label.configure(text=message)
            if "Error" in message:
                self.status_label.configure(text_color="red")
            else:
                self.status_label.configure(text_color=self.current_theme["TEXT_COLOR"])
            
            self.progress_bar.set(progress)
        
        self.after(0, _update)

    def set_ui_processing_state(self, is_processing):
        self.is_processing = is_processing
        state = "disabled" if is_processing else "normal"
        
        def _update_ui():
            # Disable all inputs
            self.ref_btn_file.configure(state=state)
            self.ref_btn_folder.configure(state=state)
            self.event_btn_file.configure(state=state)
            self.event_btn_folder.configure(state=state)
            self.output_btn.configure(state=state)
            self.start_btn.configure(state=state)
            self.mode_switcher.configure(state=state) # <-- Also disable mode switcher
            
            self.progress_bar.set(0)

            if is_processing:
                # Use the button's current text
                current_text = self.start_btn.cget("text")
                self.start_btn.configure(text=f"{current_text.replace('Start ', '')}ing...")
                self.ref_entry.configure(state="disabled")
                self.event_entry.configure(state="disabled")
                self.output_entry.configure(state="disabled")
                self.status_label.configure(text="Processing started...", text_color=self.current_theme["TEXT_COLOR"])
            else:
                # Restore text based on mode
                self.on_mode_change(self.current_mode.get()) 
                self.ref_entry.configure(state="normal")
                self.event_entry.configure(state="normal")
                self.output_entry.configure(state="normal")
                self.status_label.configure(text="Ready. Select inputs to begin.", text_color=self.current_theme["DISABLED_COLOR"])
                

        self.after(0, _update_ui)

    def on_closing(self):
        if self.is_processing:
            if messagebox.askyesno("Confirm", "Processing is in progress. Are you sure you want to exit?"):
                self.destroy()
        else:
            self.destroy()

    def check_theme_change(self, event=None):
        try:
            new_theme_name = ctk.get_appearance_mode()
            if new_theme_name != self.current_theme_name:
                self.current_theme_name = new_theme_name
                self.current_theme = DARK_THEME if new_theme_name == "Dark" else LIGHT_THEME
                self.update_ui_theme()
        except Exception as e:
            pass

    def update_ui_theme(self):
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
            
        for btn in [self.ref_btn_file, self.ref_btn_folder, self.event_btn_file, self.event_btn_folder, self.output_btn, self.start_btn]:
            btn.configure(
                fg_color=self.current_theme["BTN_COLOR"],
                text_color=self.current_theme["BTN_TEXT_COLOR"],
                hover_color=self.current_theme["BTN_HOVER_COLOR"]
            )
        
        # --- NEW: Update theme for mode switcher ---
        self.mode_switcher.configure(
            selected_color=self.current_theme["BTN_COLOR"],
            selected_hover_color=self.current_theme["BTN_HOVER_COLOR"],
            text_color=self.current_theme["TEXT_COLOR"],
            text_color_disabled=self.current_theme["DISABLED_COLOR"],
            unselected_color=self.current_theme["ENTRY_COLOR"],
            unselected_hover_color=self.current_theme["MENU_COLOR"],
            fg_color=self.current_theme["ENTRY_COLOR"]
        )
        # --- END NEW ---

        self.progress_bar.configure(
            progress_color=self.current_theme["PROGRESS_COLOR"],
            fg_color=self.current_theme["ENTRY_COLOR"],
            border_color=self.current_theme["BORDER_COLOR"]
        )


if __name__ == "__main__":
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