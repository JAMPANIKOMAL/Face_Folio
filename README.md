# Face Folio: Automated Photo Organizer

A Digital Image Processing application that automatically sorts event photos into folders by recognized faces using the [face_recognition](https://github.com/ageitgey/face_recognition) library.

This application provides two modes:

1.  **Reference Sort:** You provide a folder of reference photos (e.g., `Alice.jpg`, `Bob.png`) and a folder of event photos. The app sorts the event photos into folders named `Alice` and `Bob`.
2.  **Auto-Discovery:** You provide *only* a folder of event photos. The app scans all photos, finds all unique faces, and presents them in an in-app tagging window for you to name. Once you are done tagging, it sorts the entire event folder based on the names you provided.

Unknown faces are copied to a `_NoMatches` folder.

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

-----

## About

Face Folio was developed for the Digital Image Processing (G5A23DIP) course at Rashtriya Raksha University. It uses the `face_recognition` library to generate 128-d face embeddings and sorts photos by matching faces.

### Core Flows

**1. Reference Sort Mode**

1.  Load reference images (e.g., `Name.jpg`) from a Reference Input (folder, file, or ZIP).
2.  Scan an Event Input (folder, file, or ZIP) for photos.
3.  For each event photo, detect all faces and compute their 128-d embeddings.
4.  Compare event photo embeddings to the reference database (Euclidean distance). If below the tolerance threshold (`0.65`), copy the photo to that person's folder; otherwise, copy it to `_NoMatches`.

**2. Auto-Discovery Mode**

1.  Scan an Event Input (folder, file, or ZIP) for photos.
2.  For each photo, detect all faces and compute embeddings.
3.  Compare embeddings against an internal list of "seen" faces. If a face is new (distance \> `0.65`), save a cropped portrait of it to a `_Portraits_To_Tag` folder.
4.  Once scanning is complete, the GUI displays the saved portraits one-by-one, allowing the user to enter a name for each face or skip.
5.  After the user finishes tagging, the app runs the **Reference Sort** process, using the newly-tagged portraits as the reference database.

## Features

  - Face recognition via [face_recognition](https://github.com/ageitgey/face_recognition) (using `dlib`'s ResNet model).
  - **Dual-mode operation:** "Reference Sort" for pre-existing tags and "Auto-Discovery" for new events.
  - **In-app tagging UI** for naming faces found during Auto-Discovery.
  - Automated sorting of large photo collections.
  - Support for Folders, individual Images, and **ZIP archives** as inputs.
  - GUI built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
  - Asynchronous processing to keep the UI responsive.
  - Local processing for privacy (models are downloaded via `dlib` on first run).

## DIP Methodology Focus

  - **Task:** Object recognition (faces) implemented as face verification.
  - **Model:** `face_recognition` library, which uses:
      - **Face Detection:** HOG (Histogram of Oriented Gradients) based model.
      - **Face Embeddings:** A deep ResNet model (trained on `dlib`'s 5-point face landmarks) to generate 128-d face embeddings (vectors) for each face.
  - **Decision rule:** Euclidean distance between 128-d embeddings. A match is declared if the distance is below a set tolerance. This project uses a tolerance of **`0.65`** (default is 0.6).
  - **Implementation:** `face_recognition` APIs (e.g., `face_recognition.face_encodings()`, `face_recognition.compare_faces()`).

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
│
└── dist/
```

## Installation

### End Users

Download and run the built installer: [FaceFolio-Setup-v1.0.exe](dist/FaceFolio-Setup-v1.0.exe). No Python required. The `dlib` face models will be downloaded on the first run.

### Developers

Clone and run from source:

```powershell
git clone https://github.com/JAMPANIKOMAL/Face_Folio.git
cd Face_Folio
python -m venv venv
.\venv\Scripts\activate

# Note: dlib and cmake can be difficult to install.
# It is recommended to install dlib first, e.g., via a wheel:
# pip install cmake
# pip install dlib
pip install -r requirements.txt

# Run the application
python main.py
```

Notes:

  - Python: https://www.python.org/
  - `face_recognition` repo & docs: https://github.com/ageitgey/face_recognition

## Building & Distribution

This is a 2-step process. Run these commands from the project root after activating your `venv`. See [PyInstaller docs](https://pyinstaller.org/) for details.

### Step 1 — Build main app bundle

This command packages the Python application and its dependencies into a single folder.

```powershell
# From project root with venv activated
pyinstaller --noconsole --onedir --name FaceFolio --paths "src" --add-data "assets;assets" --hidden-import "tkinter" --hidden-import "face_recognition" --hidden-import "dlib" --hidden-import "skimage" --collect-all "customtkinter" --collect-all "numpy" --collect-all "PIL" --icon "assets/app_logo.ico" main.py
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

Academic Year: 2024–2025

## Technologies

  - [Python](https://www.python.org/)
  - [face_recognition](https://github.com/ageitgey/face_recognition)
  - [dlib](http://dlib.net/)
  - [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (GUI)
  - [PyInstaller](https://pyinstaller.org/) (packaging)

## Acknowledgments

  - `face_recognition` contributors — https://github.com/ageitgey/face_recognition
  - `dlib` developer — http://dlib.net/
  - CustomTkinter developers — https://github.com/TomSchimansky/CustomTkinter