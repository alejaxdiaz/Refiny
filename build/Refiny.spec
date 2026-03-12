# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

project_root = Path(SPECPATH).parent

a = Analysis(
    [str(project_root / 'refiny' / '__main__.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / 'assets' / 'icon.png'), 'assets'),
        (str(project_root / 'assets' / 'icon_gray.png'), 'assets'),
        (str(project_root / 'assets' / 'icon.ico'), 'assets'),
    ],
    hiddenimports=[
        'win32api',
        'win32con',
        'win32gui',
        'win32clipboard',
        'pystray._win32',
        'PIL._tkinter_finder',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Refiny',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'icon.ico'),
)
