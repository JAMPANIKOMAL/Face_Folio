#!/usr/bin/env python3
"""
Face Folio - Photo Organizer Utilities
Handles file system operations: finding images and sorting (moving) them.
"""

import os
import shutil

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
    
    # os.walk will go through the main folder and all sub-folders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file's extension is in our valid list
            if file.lower().endswith(VALID_EXTENSIONS):
                full_path = os.path.join(root, file)
                image_paths.append(full_path)
                
    print(f"Found {len(image_paths)} valid images.")
    return image_paths

def sort_photos_into_folders(photo_to_people_map, output_folder):
    """
    Copies the event photos into new person-named folders based on
    the match results.
    
    Args:
        photo_to_people_map (dict):
            A dictionary like: {"path/to/image.jpg": ["Komal", "Rahul"], ...}
        output_folder (str):
            The root output directory to create the new folders in.
    """
    print("Starting final sort...")
    
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
                # Create the person-specific folder
                # e.g., "Output_Folder/Komal"
                person_folder = os.path.join(output_folder, name)
                os.makedirs(person_folder, exist_ok=True)
                
                # Copy the photo into their folder
                filename = os.path.basename(image_path)
                destination_path = os.path.join(person_folder, filename)
                
                # We copy (shutil.copy2) instead of move,
                # so a photo with two people can go in both folders.
                # We also check if it's already there to avoid re-copying.
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