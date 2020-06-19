from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time, os, glob
import hashlib

def getElement(browser, xPathString):
    try:
        element = browser.find_element_by_xpath(xPathString)
        return element
    except (NoSuchElementException) as e:
        return None

def getText(element):
    try:
        return element.get_attribute("innerHTML")
    except StaleElementReferenceException:
        return ''

def connectToBrowser(url):
    workingFolder = os.path.abspath(os.getcwd())
    mimeTypes = "application/zip,application/octet-stream,image/jpeg,application/vnd.ms-outlook,text/html,application/pdf"

    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2) #tells it not to use default Downloads directory
    profile.set_preference("browser.download.manager.showWhenStarting", False) #turns of showing download progress
    profile.set_preference("browser.download.dir", workingFolder + '\download\\') #sets the directory for downloads
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", mimeTypes) #tells Firefox to automatically download the files of the selected mime-types
    profile.set_preference("pdfjs.disabled", True); #setting pdfjs.disabled to true will prevent Firefox previewing the files.
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    profile.set_preference("browser.download.manager.useWindow", False)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)

    browser = webdriver.Firefox(firefox_profile = profile)
    browser.get("https://web.whatsapp.com/")
    return browser

def hashfile(path, blocksize = 65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()

def removeDuplicates(folder):
    list_of_files = glob.glob(folder + '/*')
    list_of_files_sorted = sorted(list_of_files, key=os.path.getctime)

    if len(list_of_files_sorted) == 0:
        return False

    duplicates = []
    newFile = list_of_files_sorted[-1]

    for f in list_of_files_sorted:
        if hashfile(newFile) == hashfile(f):
            duplicates.append(f)

    if len(duplicates) > 1:
        os.remove(newFile)
        return True
    return False

def getMostRecentFileInDownloadsFolder(folder):
    list_of_files = glob.glob(folder + '/*')
    list_of_files_sorted = sorted(list_of_files, key=os.path.getctime)

    if len(list_of_files_sorted) == 0:
        return

    return list_of_files_sorted[-1]

def checkTag(element, tag):
    if element is not None:
        try:
            if element.tag_name == tag:
                return True
            else:
                return False
        except (StaleElementReferenceException, NoSuchElementException) as e:
            return False
    return False

def checkIfIsChildren(elementFather, elementChild):
    if elementFather is None or elementChild is None:
        return False

    listChildren = []
    try:
        auxChildren = elementFather.find_elements_by_xpath(".//*")
    except (StaleElementReferenceException, NoSuchElementException) as e:
        return False
    for child in auxChildren:
        listChildren.append(child)

    if elementChild in listChildren:
        return True
    else:
        return False
