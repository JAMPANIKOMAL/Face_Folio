#!/usr/bin/env python3
"""
Face Folio - Core DIP Logic
Uses DeepFace to find and sort photos.
"""

import os
import shutil
import pandas as pd
from deepface import DeepFace

# Define the image extensions we want to process
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp')

def find_images(folder_path):
    """
    Recursively finds all valid image files in a given folder.
    
    Args:
        folder_path (str): The absolute path to the folder to scan.
        
    Returns:
        list: A list of absolute paths to all valid image files.
    """
    image_paths = []
    print(f"Scanning for images in: {folder_path}")
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(VALID_EXTENSIONS):
                full_path = os.path.join(root, file)
                image_paths.append(full_path)
                
    print(f"Found {len(image_paths)} valid images.")
    return image_paths

def run_face_analysis(ref_folder, event_image_paths, output_folder, update_status_callback):
    """
    The main analysis function. Uses DeepFace.find() to process all images.
    
    Args:
        ref_folder (str): Path to the "Reference" folder (e.g., "Komal.jpg")
        event_image_paths (list): List of paths to all event photos.
        output_folder (str): Path to the "Output" folder.
        update_status_callback (function): The UI function to update progress.
    """
    
    # --- DeepFace Configuration and Initialization ---
    update_status_callback("Step 1/2: Learning reference faces and preparing database...", 0.05)
    
    # Force DeepFace to build its representation file if it hasn't already.
    # We use event_image_paths[0] just as a dummy query image.
    try:
        DeepFace.find(
            img_path=event_image_paths[0], 
            db_path=ref_folder, 
            model_name='VGG-Face', 
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
            # DeepFace.find() returns a list of dataframes.
            # Each dataframe represents the matches found for one face detected in the query image.
            dfs = DeepFace.find(
                img_path=image_path,
                db_path=ref_folder,
                model_name='VGG-Face',
                enforce_detection=False,
                silent=True
            )
            
            found_names_in_this_photo = set()

            # Iterate over the list of DataFrames returned by DeepFace.find()
            for df in dfs:
                if not df.empty:
                    # In each non-empty DataFrame, the 'identity' column contains the file path
                    # of the reference image match. We take the TOP result.
                    identity_path = df['identity'].iloc[0]
                    
                    # Extract the person's name from the reference file path
                    name = os.path.splitext(os.path.basename(identity_path))[0]
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
                    shutil.copy2(image_path, destination_path)
                    
    # Copy photos with no matches
    # We check the original event folder path (from the first image's directory)
    if event_image_paths:
        original_event_dir = os.path.dirname(event_image_paths[0])
        for image_path in find_images(original_event_dir):
            if image_path not in all_matched_photos:
                filename = os.path.basename(image_path)
                destination_path = os.path.join(unknown_folder, filename)
                if not os.path.exists(destination_path):
                    shutil.copy2(image_path, destination_path)

    print("Sorting complete.")