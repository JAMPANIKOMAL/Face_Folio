# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# This collects files from the 'src' directory, treating it as a package.
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/app_logo.ico', 'assets'),
        ('assets/app_logo.png', 'assets'),
        ('src', 'src'), # Include the entire source folder
    ],
    hiddenimports=[
        'customtkinter',
        'deepface',
        'tensorflow',
        'tensorflow-cpu',
        'tf_keras',
        'pandas._libs.tslibs.base', 
        'retinaface', 
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# Collect all binaries (DLLs) needed for DeepFace/TensorFlow/OpenCV/CustomTkinter
collected_binaries = a.binaries + collect_all('customtkinter')[0] + collect_all('cv2')[0] + collect_all('tensorflow')[0]

exe = EXE(
    pyz,
    a.scripts,
    collected_binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FaceFolio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Must be False for a GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_logo.ico' 
)