# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# --- IMPORTANT: The dist/FaceFolio folder MUST exist before running this spec ---

# 1. Collect all the components of the installer and the app bundle
a = Analysis(
    ['installer_ui.py'], # The entry point for the setup wizard
    pathex=['.'],
    binaries=[],
    datas=[
        # Include the entire built FaceFolio executable folder from dist/
        # PyInstaller looks for the dist folder relative to the project root (where this file is)
        ('../dist/FaceFolio', 'FaceFolio'), 
        
        # Include the uninstaller and assets
        ('uninstaller_ui.py', '.'), # Copy uninstaller to the same folder as installer_ui.py
        ('../assets/app_logo.ico', 'assets'),
    ],
    hiddenimports=['win32com.client', 'winreg', 'sys', 'customtkinter'], 
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

# 2. Build the final installer EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FaceFolio-Setup-v1.0', 
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, 
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../assets/app_logo.ico'
)