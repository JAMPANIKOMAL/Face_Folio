# Face Folio: Automated Photo Organizer

A Digital Image Processing application that automatically sorts event photos into folders by recognized faces using DeepFace (VGG-Face). Unknown faces are copied to a `_NoMatches` folder.

## Table of Contents

- About
- Features
- DIP Methodology Focus
- Project Structure
- Installation
- Building & Distribution
- Team
- Technologies
- Acknowledgments

---

## About

Face Folio was developed for the Digital Image Processing (G5A23DIP) course at Rashtriya Raksha University. It uses DeepFace to generate face embeddings and sorts photos by matching event-photo faces against a reference database of labeled images.

Core flow:
1. Load reference images (e.g., `Name.jpg`) from a Reference Folder.
2. Scan an Event Folder for photos.
3. For each photo, detect faces and compute embeddings.
4. Compare embeddings to the reference database (Euclidean distance). If below threshold, copy to a person's folder; otherwise copy to `_NoMatches`.

## Features

- DeepFace (VGG-Face) based face recognition
- Automated sorting of large photo collections
- CustomTkinter-based UI
- Asynchronous processing to keep the UI responsive
- Local processing for privacy
- Model downloaded on first run (approx. 550 MB)

## DIP Methodology Focus

- Task: Object Recognition (faces) implemented as face verification.
- Model: VGG-Face within DeepFace — produces embedding vectors for each detected face.
- Decision rule: Euclidean distance between embeddings; matches if distance < threshold.
- Implementation: face analysis uses DeepFace APIs (e.g., `DeepFace.find()` / `DeepFace.verify()`).

## Project Structure

```
Face_Folio/
│
├── main.py
├── requirements.txt
│
├── src/
│   ├── core/
│   │   └── photo_organizer.py
│   └── ui/
│       └── main_window.py
│
├── assets/
│   ├── app_logo.ico
│   └── app_logo.png
│
├── installer/
│   ├── installer_ui.py
│   ├── uninstaller_ui.py
│   └── FaceFolio_Complete_Setup.spec
│
├── FaceFolio.spec
└── dist/
```

## Installation

### End Users
Download and run the built installer: `FaceFolio-Setup-v1.0.exe`. No Python required. The DeepFace model will download on first run.

### Developers
Clone and run from source:

```powershell
git clone https://github.com/JAMPANIKOMAL/Face_Folio.git
cd Face_Folio
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Run the application
python main.py
```

Note: DeepFace/TensorFlow may require a specific Python version (e.g., 3.11) for best stability.

## Building & Distribution

Step 1 — Build main app bundle:

```powershell
# From project root with venv activated
pyinstaller FaceFolio.spec
# Output: dist/FaceFolio/FaceFolio.exe
```

Step 2 — Build the complete setup:

```powershell
# Ensure dist/FaceFolio exists
pyinstaller installer/FaceFolio_Complete_Setup.spec
# Output: installer/dist/FaceFolio-Setup-v1.0.exe
```

## Team

Primary Developer: Jampani Komal

Roles (example):
- DIP / Model Specialist — DeepFace integration, comparison logic
- Application & Integration Engineer — GUI, installer scripts, packaging
- Documentation & Testing Lead — Project report and validation

Academic Year: 2024–2025

## Technologies

- Python
- DeepFace / TensorFlow / VGG-Face
- CustomTkinter (GUI)
- PyInstaller (packaging)

## Acknowledgments

- DeepFace contributors
- CustomTkinter developers

<!-- end -->
