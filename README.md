# Face Folio: Automated Photo Organizer

A Digital Image Processing application that automatically sorts event photos into folders by recognized faces using [DeepFace (VGG‑Face)](https://github.com/serengil/deepface). Unknown faces are copied to a `_NoMatches` folder.

## Table of Contents

- [About](#about)  
- [Features](#features)  
- [DIP Methodology Focus](#dip-methodology-focus)  
- [Project Structure](#project-structure)  
- [Installation](#installation)  
    - [End Users](#end-users)  
    - [Developers](#developers)  
- [Building & Distribution](#building--distribution)  
- [Team](#team)  
- [Technologies](#technologies)  
- [Acknowledgments](#acknowledgments)

---

## About

Face Folio was developed for the Digital Image Processing (G5A23DIP) course at Rashtriya Raksha University. It uses DeepFace to generate face embeddings and sorts photos by matching event-photo faces against a reference database of labeled images.

Core flow:
1. Load reference images (e.g., `Name.jpg`) from a Reference Folder.
2. Scan an Event Folder for photos.
3. For each photo, detect faces and compute embeddings.
4. Compare embeddings to the reference database (Euclidean distance). If below threshold, copy to a person's folder; otherwise copy to `_NoMatches`.

## Features

- Face recognition via [DeepFace (VGG‑Face)](https://github.com/serengil/deepface)  
- Automated sorting of large photo collections  
- GUI built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)  
- Asynchronous processing to keep the UI responsive  
- Local processing for privacy (models downloaded on first run; ~550 MB)  

## DIP Methodology Focus

- Task: Object recognition (faces) implemented as face verification.  
- Model: VGG‑Face embeddings (via DeepFace). See VGG‑Face paper: https://www.robots.ox.ac.uk/~vgg/publications/2015/parkhi15/  
- Decision rule: Euclidean distance between embeddings; match if distance < threshold.  
- Implementation: DeepFace APIs (e.g., `DeepFace.find()` / `DeepFace.verify()`).

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

Notes:
- Python: https://www.python.org/ (use recommended version, e.g., 3.11 for TensorFlow compatibility).  
- DeepFace repo & docs: https://github.com/serengil/deepface

## Building & Distribution

This is a 2-step process. Run these commands from the project root after activating your `venv`. See [PyInstaller docs](https://pyinstaller.org/) for details.

### Step 1 — Build main app bundle

This command packages the Python application and its dependencies into a single folder.

```powershell
# From project root with venv activated
pyinstaller --noconsole --onedir --name FaceFolio --paths "src" --add-data "assets;assets" --hidden-import "tkinter" --hidden-import "tensorflow-cpu" --hidden-import "cv2" --hidden-import "deepface" --collect-all "customtkinter" --collect-all "numpy" --collect-all "PIL" --icon "assets/app_logo.ico" main.py
```

Output: `dist/FaceFolio` folder.

### Step 2 — Build the complete setup installer

This command packages the app bundle from Step 1 into a single-file setup wizard (`.exe`). You must run Step 1 first so `dist/FaceFolio` exists.

```powershell
pyinstaller --noconsole --onefile --name FaceFolio-Setup-v1.0 --add-data "dist/FaceFolio;FaceFolio" --add-data "installer/uninstaller_ui.py;." --hidden-import "win32com.client" --hidden-import "win32com.shell" --hidden-import "pywintypes" --hidden-import "winreg" --hidden-import "shutil" --collect-all "customtkinter" --icon "assets/app_logo.ico" installer/installer_ui.py --uac-admin
```

Output: `dist/FaceFolio-Setup-v1.0.exe`.

## Team

Primary Developer: Jampani Komal

Roles (example):
- DIP / Model Specialist — DeepFace integration, comparison logic  
- Application & Integration Engineer — GUI, installer scripts, packaging  
- Documentation & Testing Lead — Project report and validation

Academic Year: 2024–2025

## Technologies

- [Python](https://www.python.org/)  
- [DeepFace](https://github.com/serengil/deepface) / [TensorFlow](https://www.tensorflow.org/) / VGG‑Face  
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (GUI)  
- [PyInstaller](https://pyinstaller.org/) (packaging)

## Acknowledgments

- DeepFace contributors — https://github.com/serengil/deepface  
- CustomTkinter developers — https://github.com/TomSchimansky/CustomTkinter

<!-- end list -->