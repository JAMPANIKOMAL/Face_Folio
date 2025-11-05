#!/usr/bin/env python3
"""
Face Folio - Core Photo Organization Logic
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This module contains the core face recognition and photo sorting logic using the
face_recognition library (powered by dlib's ResNet-based model).

Key Features:
- Reference-based photo sorting: Sort photos based on known reference faces
- Auto-discovery mode: Find unique faces in photos and tag them interactively
- ZIP file support: Process photos from ZIP archives
- 128-dimensional face embedding generation using dlib
- Euclidean distance-based face matching with configurable tolerance

Face Recognition Pipeline:
1. Load image file
2. Detect face locations using HOG (Histogram of Oriented Gradients)
3. Generate 128-d face embeddings using dlib's ResNet model
4. Compare embeddings using Euclidean distance
5. Match faces based on tolerance threshold (0.65 by default)

Author: Jampani Komal
Version: 1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import shutil
import zipfile
import tempfile
from pathlib import Path
import face_recognition

VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp')

FACE_MATCH_TOLERANCE = 0.65


def _load_reference_encodings(image_paths, progress_callback):
    """
    Load face encodings from reference images.
    
    Processes a list of reference images and extracts face encodings.
    The person's name is derived from the filename (e.g., "Alice.jpg" -> "Alice").
    Only the first detected face in each image is used.
    
    Args:
        image_paths (list): List of absolute paths to reference images
        progress_callback (callable): Function to report progress (message, progress_value)
        
    Returns:
        tuple: (list of names, list of face encodings)
    """
    known_face_encodings = []
    known_face_names = []
    total = len(image_paths)

    for i, image_path in enumerate(image_paths):
        filename = os.path.basename(image_path)
        name = os.path.splitext(filename)[0]
        
        if progress_callback:
            progress_callback(f"Learning face: {name} ({i+1}/{total})", 0.3 + (0.3 * (i / total)))
        
        print(f"[DEBUG] Learning reference: {image_path}")
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
    Sort event photos based on reference faces (Reference Sort Mode).
    
    This function performs the main photo sorting operation:
    1. Loads reference images and learns faces
    2. Scans event photos for faces
    3. Matches event photo faces against reference database
    4. Copies photos to person-specific folders or _NoMatches folder
    
    Args:
        ref_input_path (str): Path to reference folder/file/ZIP
        event_input_path (str): Path to event photos folder/file/ZIP
        output_folder (str): Destination folder for sorted photos
        update_status_callback (callable): Function to update UI status
        
    Raises:
        Exception: If no valid images found or no faces detected in references
    """
    temp_dirs_to_clean = []
    
    try:
        update_status_callback("Step 1/3: Loading reference images...", 0.1)
        ref_image_paths, ref_temp_dir = find_images(ref_input_path)
        if ref_temp_dir:
            temp_dirs_to_clean.append(ref_temp_dir)
        
        if not ref_image_paths:
            raise Exception("No valid reference images found.")

        update_status_callback("Step 2/3: Finding all event photos...", 0.2)
        event_image_paths, event_temp_dir = find_images(event_input_path)
        if event_temp_dir:
            temp_dirs_to_clean.append(event_temp_dir)
        
        if not event_image_paths:
            raise Exception("No valid event images found.")

        update_status_callback("Step 3/3: Learning reference faces...", 0.3)
        known_names, known_encodings = _load_reference_encodings(ref_image_paths, update_status_callback)

        if not known_encodings:
            raise Exception("No faces could be learned from the reference images.")
            
        update_status_callback(f"Step 3/3: Analyzing {len(event_image_paths)} event photos...", 0.6)

        unknown_folder = os.path.join(output_folder, "_NoMatches")
        os.makedirs(unknown_folder, exist_ok=True)
        person_folders = {}
        for name in known_names:
            folder_path = os.path.join(output_folder, name)
            os.makedirs(folder_path, exist_ok=True)
            person_folders[name] = folder_path

        total = len(event_image_paths)
        for i, image_path in enumerate(event_image_paths):
            filename = os.path.basename(image_path)
            progress = 0.6 + (0.4 * (i / total))
            update_status_callback(f"Analyzing {filename} ({i+1}/{total})", progress)
            
            print(f"[DEBUG] Processing event file: {image_path}")
            try:
                unknown_image = face_recognition.load_image_file(image_path)
                unknown_encodings = face_recognition.face_encodings(unknown_image)
                
                found_in_photo = set()
                
                for encoding in unknown_encodings:
                    matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=FACE_MATCH_TOLERANCE)
                    
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
                    pass

    finally:
        for d in temp_dirs_to_clean:
            print(f"Cleaning up temporary directory: {d}")
            shutil.rmtree(d, ignore_errors=True)


def _save_portrait(image, face_location, save_path):
    """
    Extract and save a face portrait from an image.
    
    Crops the face region from the image with padding and saves it as a JPEG.
    Used in auto-discovery mode to create taggable face portraits.
    
    Args:
        image (numpy.ndarray): Source image array
        face_location (tuple): Face bounding box (top, right, bottom, left)
        save_path (str): Destination path for the cropped portrait
    """
    top, right, bottom, left = face_location
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
    Discover and extract unique faces from event photos (Auto-Discovery Mode).
    
    Scans all event photos, identifies unique faces, and saves cropped portraits
    for manual tagging. Uses face embedding comparison to avoid duplicate portraits.
    
    Process:
    1. Scan all event photos
    2. Detect faces in each photo
    3. Compare against previously found faces (using tolerance)
    4. Save new unique faces as cropped portraits to _Portraits_To_Tag folder
    
    Args:
        event_input_path (str): Path to event photos folder/file/ZIP
        output_folder (str): Destination folder (portraits saved to subfolder)
        update_status_callback (callable): Function to update UI status
        
    Returns:
        list: Paths to saved portrait files for tagging
        
    Raises:
        Exception: If no valid event images found
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

            print(f"[DEBUG] Processing event file: {image_path}")
            try:
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)
                face_encodings = face_recognition.face_encodings(image, face_locations)
                
                for j, (encoding, location) in enumerate(zip(face_encodings, face_locations)):
                    if not known_face_encodings:
                        portrait_path = os.path.join(tagging_folder, f"Person_{len(portrait_files)}.jpg")
                        _save_portrait(image, location, portrait_path)
                        known_face_encodings.append(encoding)
                        portrait_files.append(portrait_path)
                        continue

                    matches = face_recognition.compare_faces(known_face_encodings, encoding, tolerance=FACE_MATCH_TOLERANCE)
                    
                    if True not in matches:
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


def find_images(input_path):
    """
    Recursively find all valid image files from various input sources.
    
    Supports three types of inputs:
    1. ZIP archives - Extracts to temp directory and scans
    2. Single image files - Returns as single-item list
    3. Folders - Recursively scans for all image files
    
    Args:
        input_path (str): Path to folder, image file, or ZIP archive
        
    Returns:
        tuple: (list of absolute image paths, temp directory path or None)
               Temp directory should be cleaned up by caller if not None
    """
    image_paths = []
    temp_dir = None
    input_path = Path(input_path)

    if input_path.suffix.lower() == '.zip':
        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(VALID_EXTENSIONS):
                        image_paths.append(os.path.join(root, file))
        except Exception as e:
            print(f"Error extracting zip: {e}")
            if temp_dir: shutil.rmtree(temp_dir, ignore_errors=True)
            return [], None
    
    elif input_path.is_file() and input_path.suffix.lower() in VALID_EXTENSIONS:
        image_paths.append(str(input_path))

    elif input_path.is_dir():
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(VALID_EXTENSIONS):
                    image_paths.append(os.path.join(root, file))
    
    print(f"Found {len(image_paths)} valid images.")
    return image_paths, temp_dir