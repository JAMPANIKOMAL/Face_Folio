#!/usr/bin/env python3
"""
Face Folio - Core Face Detection Logic
Implements DIP Unit 6: Object Recognition
"""

import face_recognition
import numpy as np
import os

def find_faces_in_image(image_path):
    """
    Loads an image, finds all faces, and computes their 128-point encodings.
    This relates to DIP Unit 6: Object Recognition (patterns and pattern classes).
    The "encoding" is the 128-dimension vector (a "pattern") that
    represents a unique face.
    
    Args:
        image_path (str): The absolute path to a single image file.
        
    Returns:
        tuple: (list of face_locations, list of face_encodings)
               - face_locations: A list of (top, right, bottom, left) tuples.
               - face_encodings: A list of 128-element numpy arrays.
    """
    try:
        # Load the image file into a numpy array
        image = face_recognition.load_image_file(image_path)
        
        # Find all face locations in the image.
        # We use "hog" (Histogram of Oriented Gradients) as it's faster
        # than "cnn" and good enough for this.
        face_locations = face_recognition.face_locations(image, model="hog")
        
        if not face_locations:
            # No faces found in this image
            return [], []
            
        # Get the 128-point face encodings (the "pattern" for each face)
        face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)
        
        return face_locations, face_encodings
        
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        # Could be a corrupt image file
        return [], []