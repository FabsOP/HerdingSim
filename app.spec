# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['run.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=['pygame', 'mutagen', 'PIL', 'numpy', 'tktooltip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HerdSim',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/sheep.ico'
)