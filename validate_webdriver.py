import os
import shutil
import subprocess

from urllib.request import urlretrieve, urlopen, ContentTooShortError
from xml.etree import ElementTree
from win32com.client import Dispatch
import pythoncom


def popen(command):
    """For pyinstaller -w"""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(command, startupinfo=startupinfo, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, stdin=subprocess.PIPE, encoding='utf8')
    return process.stdout.read()


def get_version_via_com(filename):
    parser = Dispatch("Scripting.FileSystemObject")
    try:
        version = parser.GetFileVersion(filename)
    except Exception:
        return None
    return version


def get_matched_chromedriver_version(version):
    """
    :param version: the version of chrome
    :return: the version of chromedriver
    """
    doc = urlopen('https://chromedriver.storage.googleapis.com').read()
    root = ElementTree.fromstring(doc)
    for k in root.iter('{http://doc.s3.amazonaws.com/2006-03-01}Key'):
        if k.text.find(version + '.') == 0:
            return k.text.split('/')[0]
    return


def get_driver_version():
    try:
        localpath = os.path.abspath(os.getcwd()).replace('\\', '/')
        version = popen(f'"{localpath}/chromedriver.exe" -v')
        return version.split(' ')[1]
    except (IndexError, FileNotFoundError):
        return '0.0.0.0'


def validate_chromewebdriver(logger=None):
    pythoncom.CoInitialize() # Enables use of com with threading

    if not logger:
        logger = print

    driver_version = get_driver_version()

    paths = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
    chrome_version = list(
        filter(None, [get_version_via_com(p) for p in paths]))[0]

    major_installed_version = chrome_version.split('.')[0]
    major_driver_version = driver_version.split('.')[0]

    if major_driver_version < major_installed_version:
        url_file = 'https://chromedriver.storage.googleapis.com/'

        matched_driver = get_matched_chromedriver_version(
            major_installed_version)

        file_name = 'chromedriver_win32.zip'

        logger('==========================')

        logger('Installed Chrome Version ' + chrome_version)

        if chrome_version:
            logger('Downloading new webdriver')
            while True:
                try:
                    download = urlretrieve(
                        url_file + matched_driver + '/' + file_name, file_name)
                    if download:
                        logger('Webdriver successfully downloaded')
                        break
                except ContentTooShortError:
                    logger('Download interrupted, trying again')

        logger('Extracting files')
        shutil.unpack_archive(file_name)

        logger('Files extracted, removing zip file')

        os.remove(file_name)

        logger('Done')
        logger('==========================')


if __name__ == "__main__":
    validate_chromewebdriver()
