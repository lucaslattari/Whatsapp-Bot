from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from utils import *
import itertools
import time

def sendMultipleMessages(browser, arrayContactName, arrayMessage):
    for (contact, message) in zip(arrayContactName, arrayMessage):
        searchForContact(browser, contact)
        sendSingleMessage(browser, contact, message)
        deleteInputText(browser)

def deleteInputText(browser):
    searchInputText = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')))
    searchInputText.click()
    print("Cliquei no campo de busca de contato.")
    time.sleep(3)
    searchInputText.send_keys(Keys.CONTROL, 'a')
    print("Selecionei o nome anterior.")
    time.sleep(3)
    searchInputText.send_keys(Keys.BACKSPACE)
    print("Apaguei o nome do contato anterior da busca.")
    time.sleep(5)

def searchForContact(browser, contactName):
    searchInputText = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')))
    searchInputText.click()
    print("Cliquei no campo de busca de contato.")
    time.sleep(3)
    searchInputText.send_keys(contactName)
    print("Digitei o nome do contato: " + contactName + ".")
    time.sleep(3)
    searchInputText.send_keys(Keys.ENTER)
    print("Apertei ENTER.")
    time.sleep(3)

def sendSingleMessage(browser, contactName, message):
    messageInputText = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]')))
    messageInputText.send_keys(message)
    print("Escrevi a mensagem. Aperte ENTER para confirmar o envio!")
    time.sleep(3)
    messageInputText.send_keys(Keys.ENTER)
    print("Mensagem enviada!")
    time.sleep(3)
