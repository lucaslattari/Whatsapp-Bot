from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from utils import *
import itertools
import time

def sendMultipleMessages(browser, arrayContactName, arrayMessage):
    for (contact, message) in zip(arrayContactName, arrayMessage):
        sendSingleMessage(browser, contact, message)
        deleteInputText(browser)

def deleteInputText(browser):
    searchInputText = getElementIfExists(browser, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')
    searchInputText.click()
    searchInputText.send_keys(Keys.CONTROL, 'a')
    searchInputText.send_keys(Keys.BACKSPACE)
    time.sleep(5)

def sendSingleMessage(browser, contactName, message):
    searchInputText = getElementIfExists(browser, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')
    searchInputText.click()
    searchInputText.send_keys(contactName)
    time.sleep(5)

    contactElement = getContactElement(browser)
    contactElement.click()
    time.sleep(5)

    messageInputText = getElementIfExists(browser, '/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]')
    messageInputText.click()
    messageInputText.send_keys(message)
    messageInputText.send_keys(Keys.ENTER)
    time.sleep(5)
