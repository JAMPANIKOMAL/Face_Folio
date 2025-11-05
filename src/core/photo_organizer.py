#!/usr/bin/env python3
"""
Face Folio - Core DIP Logic
Uses DeepFace to find and sort photos.
"""

import os
import shutil
import pandas as pd
from deepface import DeepFace
from pathlib import Path
import zipfile
import tempfile

# Define the image extensions we want to process
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp')

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

def run_face_analysis(ref_input_path, event_input_path, output_folder, update_status_callback):
    """
    The main analysis function. Uses DeepFace.find() to process all images.
    """
    
    temp_dirs_to_clean = []
    ref_db_path = str(ref_input_path)
    
    try:
        # 1. Process Reference Input (Folder/File/ZIP)
        ref_image_paths, ref_temp_dir = find_images(ref_input_path)
        if ref_temp_dir: 
            temp_dirs_to_clean.append(ref_temp_dir)
            ref_db_path = ref_temp_dir
        
        # --- BUG FIX: Handle single image reference ---
        # If input is a single file, create a temp DB for DeepFace
        elif Path(ref_input_path).is_file() and Path(ref_input_path).suffix.lower() in VALID_EXTENSIONS:
            ref_db_temp_dir = tempfile.mkdtemp()
            temp_dirs_to_clean.append(ref_db_temp_dir)
            
            # Use file stem as the person's name
            person_name = Path(ref_input_path).stem
            person_folder = os.path.join(ref_db_temp_dir, person_name)
            os.makedirs(person_folder)
            
            # Copy the image into the named folder
            shutil.copy(ref_input_path, person_folder)
            
            ref_db_path = ref_db_temp_dir
            print(f"Created temporary reference DB for single file at: {ref_db_path}")
        # --- END BUG FIX ---
        
        elif not Path(ref_input_path).is_dir():
             raise Exception("Reference input must be a valid folder, image file, or ZIP archive.")


        # 2. Process Event Input (Folder/File/ZIP)
        event_image_paths, event_temp_dir = find_images(event_input_path)
        if event_temp_dir: temp_dirs_to_clean.append(event_temp_dir)

        if not event_image_paths:
            raise Exception("No valid images found in the Event Input.")

        
        # --- DeepFace Configuration and Initialization ---
        update_status_callback("Step 1/2: Learning reference faces and preparing database...", 0.05)
        
        # Force DeepFace to build its representation file if it hasn't already.
        # We use event_image_paths[0] just as a dummy query image.
        try:
            DeepFace.find(
                img_path=event_image_paths[0], 
                db_path=ref_db_path, 
                model_name='VGG-Face',
                # --- !! CRITICAL FIX !! ---
                distance_metric='euclidean_l2',
                enforce_detection=False,
                silent=True 
            )
        except Exception as e:
            # Ignore first attempt error, as it's just meant to initialize the DB
            pass

        update_status_callback(f"Step 1/2: Reference database ready. Starting photo analysis...", 0.2)
        
        total_images = len(event_image_paths)
        photo_to_people_map = {}
        
        # --- Step 2: Loop through every event photo and match it ---
        for i, image_path in enumerate(event_image_paths):
            filename = os.path.basename(image_path)
            progress = 0.2 + (0.6 * (i / total_images)) 
            
            update_status_callback(
                f"Step 2/2: Analyzing {filename} ({i+1}/{total_images})...", 
                progress
            )
            
            try:
                dfs = DeepFace.find(
                    img_path=image_path,
                    db_path=ref_db_path, # Use the path derived from the input
                    model_name='VGG-Face',
                    # --- !! CRITICAL FIX !! ---
                    distance_metric='euclidean_l2',
                    enforce_detection=False,
                    silent=True
                )
                
                found_names_in_this_photo = set()

                for df in dfs:
                    if not df.empty:
                        # Get the identity path of the top match
                        identity_path = Path(df['identity'].iloc[0])
                        
                        # FIX: Extract the person's name using the parent folder name
                        # DeepFace uses the folder containing the image as the identity.
                        name = identity_path.parent.name
                        
                        # This fix is now more robust due to the single-file-handler
                        if name == Path(ref_db_path).name:
                             name = identity_path.stem 
                             
                        found_names_in_this_photo.add(name)

                if found_names_in_this_photo:
                    print(f"Matched {list(found_names_in_this_photo)} in {filename}")
                    photo_to_people_map[image_path] = list(found_names_in_this_photo)
                else:
                     photo_to_people_map[image_path] = [] 
                     
            except Exception as e:
                print(f"Warning: Skipping {filename} due to processing error: {e}")
                photo_to_people_map[image_path] = [] 

        # --- Step 3: Sort the files based on the results (Move to new folders) ---
        update_status_callback("Sorting files into output folders...", 0.9)
        
        unknown_folder = os.path.join(output_folder, "_NoMatches")
        os.makedirs(unknown_folder, exist_ok=True)
        
        all_matched_photos = set()

        # Copy photos for recognized people
        for image_path, names in photo_to_people_map.items():
            if names:
                all_matched_photos.add(image_path)
                for name in names:
                    person_folder = os.path.join(output_folder, name)
                    os.makedirs(person_folder, exist_ok=True)
                    
                    filename = os.path.basename(image_path)
                    destination_path = os.path.join(person_folder, filename)
                    
                    if not os.path.exists(destination_path):
                        # Use shutil.copy for robustness against permissions
                        shutil.copy(image_path, destination_path)
                        
        # Copy photos with no matches (only photos from the event input that weren't matched)
        for image_path in event_image_paths:
            if image_path not in all_matched_photos:
                filename = os.path.basename(image_path)
                destination_path = os.path.join(unknown_folder, filename)
                if not os.path.exists(destination_path):
                    shutil.copy(image_path, destination_path)

        print("Sorting complete.")

    finally:
        # --- BUG FIX: Cleanup ---
        # Move cleanup to finally block to ensure it runs even if analysis fails
        for d in temp_dirs_to_clean:
            print(f"Cleaning up temporary directory: {d}")
            shutil.rmtree(d, ignore_errors=True)