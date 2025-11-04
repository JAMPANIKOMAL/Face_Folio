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
    
    # DeepFace.find() builds a database (models) for the ref_folder.
    # We must tell it to use the "VGG-Face" model, which is the default.
    # This will pre-process the reference folder.
    update_status_callback("Step 1/2: Learning reference faces...", 0.05)
    
    # This command forces DeepFace to build its model representations for the ref_folder
    # It might download models on the first run.
    try:
        # We find a "dummy" file against the database to force it to build
        # This is a standard way to initialize DeepFace's database
        DeepFace.find(
            img_path=event_image_paths[0], 
            db_path=ref_folder, 
            model_name='VGG-Face', 
            enforce_detection=False
        )
    except Exception as e:
        # This might fail if the first image has no face, which is fine
        # We are just trying to initialize the model.
        print(f"DeepFace init (this is normal): {e}")

    update_status_callback(f"Step 1/2: Reference database built. Starting analysis...", 0.2)
    
    total_images = len(event_image_paths)
    found_matches = False
    
    # This will hold our final results
    # {"path/to/image.jpg": ["Komal", "Rahul"], ...}
    photo_to_people_map = {}
    
    # --- Step 2: Loop through every event photo and match it ---
    for i, image_path in enumerate(event_image_paths):
        filename = os.path.basename(image_path)
        progress = 0.2 + (0.6 * (i / total_images)) # This step is 60% of the work
        
        update_status_callback(
            f"Step 2/2: Analyzing {filename} ({i+1}/{total_images})...", 
            progress
        )
        
        try:
            # This is the core DIP logic!
            # It compares one "needle" (image_path) against the "haystack" (ref_folder)
            # dfs = "DataFrames"
            dfs = DeepFace.find(
                img_path=image_path,
                db_path=ref_folder,
                model_name='VGG-Face',
                enforce_detection=False # Don't crash if no face is found
            )
            
            # dfs is a list of DataFrames. We only care about the first one.
            # This DataFrame has an 'identity' column with paths to the matches.
            # e.g., "C:/.../Reference/Komal.jpg"
            if not dfs[0].empty:
                # Get the 'identity' column and remove duplicates
                identities = dfs[0]['identity'].unique()
                
                # Get the names from the file paths
                names = set()
                for id_path in identities:
                    # "C:/.../Reference/Komal.jpg" -> "Komal"
                    name = os.path.splitext(os.path.basename(id_path))[0]
                    names.add(name)
                
                if names:
                    print(f"Found {list(names)} in {filename}")
                    photo_to_people_map[image_path] = list(names)
                    found_matches = True
                else:
                    photo_to_people_map[image_path] = [] # Found a face, but no match
            else:
                 photo_to_people_map[image_path] = [] # No faces found
                 
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            photo_to_people_map[image_path] = [] # Error on this file, list as no match

    # --- Step 3: Sort the files based on the results ---
    if not found_matches:
        print("No matches found in any photos.")
        
    update_status_callback("Sorting files into output folders...", 0.9)
    
    # We will also create a folder for all photos that had
    # no recognized people in them.
    unknown_folder = os.path.join(output_folder, "_NoMatches")
    os.makedirs(unknown_folder, exist_ok=True)
    
    all_matched_photos = set()

    # First, copy photos for recognized people
    for image_path, names in photo_to_people_map.items():
        if names:
            all_matched_photos.add(image_path)
            for name in names:
                # "Output_Folder/Komal"
                person_folder = os.path.join(output_folder, name)
                os.makedirs(person_folder, exist_ok=True)
                
                filename = os.path.basename(image_path)
                destination_path = os.path.join(person_folder, filename)
                
                if not os.path.exists(destination_path):
                    shutil.copy2(image_path, destination_path)
                    
    # Second, copy photos with no matches
    for image_path in photo_to_people_map.keys():
        if image_path not in all_matched_photos:
            filename = os.path.basename(image_path)
            destination_path = os.path.join(unknown_folder, filename)
            if not os.path.exists(destination_path):
                shutil.copy2(image_path, destination_path)

    print("Sorting complete.")