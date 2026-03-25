# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['birth.py'],
    pathex=[],
    binaries=[],
    datas=[('aa.jpg', '.'), ('bb.jpg', '.'), ('cc.jpg', '.'), ('Rayvanny_Happy Birthday.mp4', '.'), ('Rayvanny_Happy Birthday.mp3', '.')],
    hiddenimports=['vlc', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='birth',
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
)
