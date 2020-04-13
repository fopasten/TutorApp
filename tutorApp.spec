# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['tutorApp.py'],
             pathex=['C:\\Users\\felipe.pasten\\OneDrive - UNIVERSIDAD ANDRES BELLO\\Repositorio_Felipe_Pasten\\Tecnologías para el Aprendizaje\\PYTHON-UNAB\\SELENIUM\\App Tutores'],
             binaries=[ ('C:\\Users\\felipe.pasten\\OneDrive - UNIVERSIDAD ANDRES BELLO\\Repositorio_Felipe_Pasten\\Tecnologías para el Aprendizaje\\PYTHON-UNAB\\SELENIUM\\App Tutores\\chromedriver.exe', '.') ],
             datas=[ ('C:\\Users\\felipe.pasten\\OneDrive - UNIVERSIDAD ANDRES BELLO\\Repositorio_Felipe_Pasten\\Tecnologías para el Aprendizaje\\PYTHON-UNAB\\SELENIUM\\App Tutores\\banner.png', '.'), ('C:\\Users\\felipe.pasten\\OneDrive - UNIVERSIDAD ANDRES BELLO\\Repositorio_Felipe_Pasten\\Tecnologías para el Aprendizaje\\PYTHON-UNAB\\SELENIUM\\App Tutores\\icon.png', '.') ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='App Tutores v1',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='App Tutores v1')
