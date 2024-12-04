# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['D:/PrayPlanner-app/src/main.py'],  
    pathex=['D:/PrayPlanner-app/src'],
    binaries=[],
    datas=[
        ('D:/Anaconda/Lib/site-packages/sv_ttk', 'sv_ttk'),
        ('D:/Anaconda/Lib/site-packages/ttkthemes', 'ttkthemes')
    ],
    hiddenimports=[
        'sv_ttk',
        'ttkthemes',
        'win10toast',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'bs4',
        'datetime',
        'tkinter',
        'pytz',
        'babel.numbers'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PrayPlanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    uac_admin=False,
    icon='logo.ico' 
)