#!/usr/bin/env python3
"""
Face Folio - Core Logic
(Restored from v1.0 prototype)
"""

import os
import shutil
import zipfile
import tempfile
from pathlib import Path
import face_recognition

# Define the image extensions we want to process
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp')

# ---
# --- FEATURE 1: REFERENCE-BASED SORTING ---
# --- (Restored from old core.py) ---
# ---

def _load_reference_encodings(image_paths, progress_callback):
    """
    Helper function to load encodings from a list of reference image paths.
    The name is derived from the image's filename (e.g., "Alice.jpg" -> "Alice")
    """
    known_face_encodings = []
    known_face_names = []
    total = len(image_paths)

    for i, image_path in enumerate(image_paths):
        filename = os.path.basename(image_path)
        name = os.path.splitext(filename)[0]
        
        if progress_callback:
            progress_callback(f"Learning face: {name} ({i+1}/{total})", 0.3 + (0.3 * (i / total)))
        
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(name)
            else:
                print(f"Warning: No face found in reference image {filename}")
        except Exception as e:
            print(f"Error loading reference {filename}: {e}")
            
    return known_face_names, known_face_encodings

def run_reference_sort(ref_input_path, event_input_path, output_folder, update_status_callback):
    """
    Main function for sorting photos based on a reference input.
    """
    temp_dirs_to_clean = []
    
    try:
        # 1. Process Reference Input (Folder/File/ZIP)
        update_status_callback("Step 1/3: Loading reference images...", 0.1)
        ref_image_paths, ref_temp_dir = find_images(ref_input_path)
        if ref_temp_dir:
            temp_dirs_to_clean.append(ref_temp_dir)
        
        if not ref_image_paths:
            raise Exception("No valid reference images found.")

        # 2. Process Event Input (Folder/File/ZIP)
        update_status_callback("Step 2/3: Finding all event photos...", 0.2)
        event_image_paths, event_temp_dir = find_images(event_input_path)
        if event_temp_dir:
            temp_dirs_to_clean.append(event_temp_dir)
        
        if not event_image_paths:
            raise Exception("No valid event images found.")

        # 3. Load known faces
        update_status_callback("Step 3/3: Learning reference faces...", 0.3)
        known_names, known_encodings = _load_reference_encodings(ref_image_paths, update_status_callback)

        if not known_encodings:
            raise Exception("No faces could be learned from the reference images.")
            
        update_status_callback(f"Step 3/3: Analyzing {len(event_image_paths)} event photos...", 0.6)

        # 4. Create output folders
        unknown_folder = os.path.join(output_folder, "_NoMatches")
        os.makedirs(unknown_folder, exist_ok=True)
        person_folders = {}
        for name in known_names:
            folder_path = os.path.join(output_folder, name)
            os.makedirs(folder_path, exist_ok=True)
            person_folders[name] = folder_path

        # 5. Loop through event photos and sort
        total = len(event_image_paths)
        for i, image_path in enumerate(event_image_paths):
            filename = os.path.basename(image_path)
            progress = 0.6 + (0.4 * (i / total))
            update_status_callback(f"Analyzing {filename} ({i+1}/{total})", progress)
            
            try:
                unknown_image = face_recognition.load_image_file(image_path)
                unknown_encodings = face_recognition.face_encodings(unknown_image)
                
                found_in_photo = set()
                
                for encoding in unknown_encodings:
                    matches = face_recognition.compare_faces(known_encodings, encoding)
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_names[first_match_index]
                        found_in_photo.add(name)
                
                if found_in_photo:
                    for name in found_in_photo:
                        dest_path = os.path.join(person_folders[name], filename)
                        if not os.path.exists(dest_path):
                            shutil.copy(image_path, dest_path)
                else:
                    dest_path = os.path.join(unknown_folder, filename)
                    if not os.path.exists(dest_path):
                        shutil.copy(image_path, dest_path)
                        
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                try:
                    dest_path = os.path.join(unknown_folder, filename)
                    if not os.path.exists(dest_path):
                        shutil.copy(image_path, dest_path)
                except Exception:
                    pass # Failsafe

    finally:
        # 6. Cleanup
        for d in temp_dirs_to_clean:
            print(f"Cleaning up temporary directory: {d}")
            shutil.rmtree(d, ignore_errors=True)


# ---
# --- FEATURE 2: AUTOMATIC DISCOVERY ---
# --- (Restored from old core.py) ---
# ---

def _save_portrait(image, face_location, save_path):
    """Crops and saves a portrait of a found face."""
    top, right, bottom, left = face_location
    # Add padding
    top = max(0, top - 50)
    left = max(0, left - 50)
    bottom = min(image.shape[0], bottom + 50)
    right = min(image.shape[1], right + 50)
    
    face_image = image[top:bottom, left:right]
    
    from PIL import Image
    pil_image = Image.fromarray(face_image)
    pil_image.save(save_path)

def run_auto_discovery(event_input_path, output_folder, update_status_callback):
    """
    Finds all unique faces in an event, saves them for tagging,
    and returns a list of paths for the UI.
    """
    temp_dirs_to_clean = []
    
    try:
        update_status_callback("Step 1/2: Finding all event photos...", 0.1)
        event_image_paths, event_temp_dir = find_images(event_input_path)
        if event_temp_dir:
            temp_dirs_to_clean.append(event_temp_dir)
        
        if not event_image_paths:
            raise Exception("No valid event images found.")
            
        tagging_folder = os.path.join(output_folder, "_Portraits_To_Tag")
        if os.path.exists(tagging_folder):
            shutil.rmtree(tagging_folder)
        os.makedirs(tagging_folder)

        known_face_encodings = []
        portrait_files = []
        
        total = len(event_image_paths)
        update_status_callback(f"Step 2/2: Analyzing {total} photos for unique faces...", 0.3)
        
        for i, image_path in enumerate(event_image_paths):
            filename = os.path.basename(image_path)
            progress = 0.3 + (0.7 * (i / total))
            update_status_callback(f"Analyzing {filename} ({i+1}/{total})", progress)

            try:
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)
                face_encodings = face_recognition.face_encodings(image, face_locations)
                
                for j, (encoding, location) in enumerate(zip(face_encodings, face_locations)):
                    if not known_face_encodings:
                        # First face ever found
                        portrait_path = os.path.join(tagging_folder, f"Person_{len(portrait_files)}.jpg")
                        _save_portrait(image, location, portrait_path)
                        known_face_encodings.append(encoding)
                        portrait_files.append(portrait_path)
                        continue

                    matches = face_recognition.compare_faces(known_face_encodings, encoding)
                    
                    if True not in matches:
                        # This is a new unique face
                        portrait_path = os.path.join(tagging_folder, f"Person_{len(portrait_files)}.jpg")
                        _save_portrait(image, location, portrait_path)
                        known_face_encodings.append(encoding)
                        portrait_files.append(portrait_path)
                        
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    finally:
        for d in temp_dirs_to_clean:
            print(f"Cleaning up temporary directory: {d}")
            shutil.rmtree(d, ignore_errors=True)
            
    return portrait_files


# ---
# --- SHARED HELPER FUNCTION ---
# --- (Kept from new photo_organizer.py) ---
# ---

def find_images(input_path):
    """
    Recursively finds all valid image files from a folder, a single file, or a ZIP archive.
    
    Args:
        input_path (str): The absolute path to the folder, file, or zip.
        
    Returns:
        tuple: (list of absolute image paths, temporary extraction directory or None)
    """
    image_paths = []
    temp_dir = None
    input_path = Path(input_path)

    if input_path.suffix.lower() == '.zip':
        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Now treat the extracted temp directory as the source folder
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(VALID_EXTENSIONS):
                        image_paths.append(os.path.join(root, file))
        except Exception as e:
            print(f"Error extracting zip: {e}")
            if temp_dir: shutil.rmtree(temp_dir, ignore_errors=True)
            return [], None
    
    elif input_path.is_file() and input_path.suffix.lower() in VALID_EXTENSIONS:
        # Handle single photo input
        image_paths.append(str(input_path))

    elif input_path.is_dir():
        # Handle folder input
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(VALID_EXTENSIONS):
                    image_paths.append(os.path.join(root, file))
    
    print(f"Found {len(image_paths)} valid images.")
    return image_paths, temp_dir