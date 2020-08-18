# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['TutorApp.py'],
             pathex=['C:\\Users\\felipe.pasten\\OneDrive - UNIVERSIDAD ANDRES BELLO\\Repositorio_Felipe_Pasten\\Tecnologías para el Aprendizaje\\PYTHON-RELEASES\\TutorApp'],
             binaries=[],
             datas=[ ('C:\\Users\\felipe.pasten\\OneDrive - UNIVERSIDAD ANDRES BELLO\\Repositorio_Felipe_Pasten\\Tecnologías para el Aprendizaje\\PYTHON-RELEASES\\TutorApp\\banner.png', '.'), ('C:\\Users\\felipe.pasten\\OneDrive - UNIVERSIDAD ANDRES BELLO\\Repositorio_Felipe_Pasten\\Tecnologías para el Aprendizaje\\PYTHON-RELEASES\\TutorApp\\icon.png', '.') ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['matplotlib','colorama', 'toml', 'lazy-object-proxy', 'scipy', 'setuptools', 'hook', 'distutils', 'site', 'hooks', 'tornado', 'PIL', 'PyQt4', 'pydoc', 'pythoncom', 'pytz', 'pywintypes', 'sqlite3', 'pyz', 'pandas', 'sklearn', 'scapy', 'scrapy', 'sympy', 'kivy', 'pyramid', 'opencv', 'tensorflow', 'pipenv', 'pattern', 'mechanize', 'beautifulsoup4', 'requests', 'wxPython', 'pygi', 'pillow', 'pygame', 'pyglet', 'flask', 'django', 'pylint', 'pytube', 'odfpy', 'mccabe', 'pilkit', 'six', 'wrapt', 'astroid', 'isort'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='TutorApp v1.0.4',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
		  icon='C:\\Users\\felipe.pasten\\OneDrive - UNIVERSIDAD ANDRES BELLO\\Repositorio_Felipe_Pasten\\Tecnologías para el Aprendizaje\\PYTHON-RELEASES\\TutorApp\\icon.ico')

import shutil
shutil.copyfile('chromedriver.exe', '{0}/chromedriver.exe'.format(DISTPATH))