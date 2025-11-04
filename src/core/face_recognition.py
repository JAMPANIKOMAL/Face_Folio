#!/usr/bin/env python3
"""
Face Folio - Core Face Recognition Logic (The "Brain")
Implements DIP Unit 6: Object Recognition (decision-theoretic methods)
"""

import face_recognition
import os
import numpy as np
from core.photo_organizer import find_images
from core.face_detection import find_faces_in_image

def learn_known_faces(reference_folder, update_status_callback):
    """
    Scans the reference folder and learns the face encodings for
    each person.
    
    Args:
        reference_folder (str): Path to the folder with "Komal.jpg", etc.
        update_status_callback (function): UI function to update status.
        
    Returns:
        dict: A dictionary like {"Komal": [encoding1], "Rahul": [encoding2]}
    """
    known_faces_dict = {}
    
    # 1. Find all images in the reference folder
    reference_images = find_images(reference_folder)
    
    if not reference_images:
        raise Exception("No valid images found in the Reference Folder.")
        
    total_ref_images = len(reference_images)
    
    for i, image_path in enumerate(reference_images):
        filename = os.path.basename(image_path)
        # Get person's name from filename (e.g., "Komal.jpg" -> "Komal")
        person_name = os.path.splitext(filename)[0]
        
        update_status_callback(
            f"Step 1/4: Learning {person_name} ({i+1}/{total_ref_images})...",
            0.0 + (0.25 * (i / total_ref_images)) # This step takes 25% of time
        )
        
        # 2. Find the face encoding for this person
        # We assume one face per reference photo
        _locations, encodings = find_faces_in_image(image_path)
        
        if encodings:
            # Add the first found encoding to our dictionary
            known_faces_dict[person_name] = encodings[0]
            print(f"Learned face for: {person_name}")
        else:
            print(f"Warning: No face found in {filename}. Skipping.")
            
    if not known_faces_dict:
        raise Exception("No faces were learned. Check your Reference Folder.")
        
    print(f"Finished learning {len(known_faces_dict)} people.")
    return known_faces_dict

def match_faces_in_photos(event_image_paths, known_faces_dict, update_status_callback):
    """
    Finds all faces in the event photos and matches them against the
    known faces.
    
    Args:
        event_image_paths (list): List of all photos to scan.
        known_faces_dict (dict): The "known faces" from the reference folder.
        update_status_callback (function): UI function to update status.
        
    Returns:
        dict: A map of {"path/to/image.jpg": ["Komal", "Rahul"], ...}
    """
    
    # Prepare the known faces data for comparison
    known_names = list(known_faces_dict.keys())
    known_encodings = list(known_faces_dict.values())
    
    photo_to_people_map = {}
    total_event_images = len(event_image_paths)

    for i, image_path in enumerate(event_image_paths):
        filename = os.path.basename(image_path)
        
        # This is the slowest part, so it takes up 50% of the progress bar
        progress = 0.25 + (0.5 * (i / total_event_images)) 
        update_status_callback(
            f"Step 3/4: Matching faces in {filename} ({i+1}/{total_event_images})...",
            progress
        )
        
        # 1. Find all faces in this one event photo
        _locations, event_face_encodings = find_faces_in_image(image_path)
        
        if not event_face_encodings:
            # No faces found in this picture, map it to empty list
            photo_to_people_map[image_path] = []
            continue
            
        found_names_in_this_photo = set()
        
        # 2. Compare each found face to all known faces
        for face_encoding in event_face_encodings:
            # This performs the core DIP logic:
            # "recognition based on decision-theoretic methods" (Unit 6)
            # It compares the 128-point vector (pattern) and finds the
            # closest match.
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
            
            # Find the distance of each match
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            # Find the best match (smallest distance)
            if True in matches:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    found_names_in_this_photo.add(name)

        # 3. Add the list of found people to our map
        photo_to_people_map[image_path] = list(found_names_in_this_photo)
        if found_names_in_this_photo:
            print(f"Matched {list(found_names_in_this_photo)} in {filename}")

    return photo_to_people_map