from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from utils import *
import time, logging, re, os, os.path
import datetime

def checkStoppingCriterion(currentDay, currentMonth, currentYear, thresholdDay, thresholdMonth, thresholdYear):
    dateMessage = datetime.date(currentYear, currentMonth, currentDay)
    dateThreshold = datetime.date(thresholdYear, thresholdMonth, thresholdDay)
    if dateMessage <= dateThreshold:
        return True
    else:
        return False

def addElementInList(listOfMessages, element):
    if element not in listOfMessages:
        listOfMessages.append(element)
        print("adicionado na lista: ", element)

def extractContactData(elementText):
    _dict = {}

    auxStr = re.search('\[(.+?), (.+?)] (.+?):', elementText)
    _time, _date, _name = auxStr.group(1), auxStr.group(2), auxStr.group(3)
    h, m = _time.split(':')
    d, M, y = _date.split('/')

    _dict["hour"] = int(h)
    _dict["minute"] = int(m)
    _dict["day"] = int(d)
    _dict["month"] = int(M)
    _dict["year"] = int(y)
    _dict["contact"] = _name

    return _dict

def checkIfIsSpanWithoutAttributes(spanElement):
    if spanElement.get_attribute("class") is None or spanElement.get_attribute("class") is '':
        if spanElement.get_attribute("dir") is None or spanElement.get_attribute("dir") is '':
            return True
    return False

def scrollToTopElement(elementArray, i):
    try:
        elementArray[i].location_once_scrolled_into_view
    except (StaleElementReferenceException, NoSuchElementException) as e:
        scrollToTopElement(elementArray, i + 1)

def getLogOfContact(browser, contactName):
    thresholdDay = 30
    thresholdMonth = 4
    thresholdYear = 2020

    searchInputText = getElementIfExists(browser, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')
    time.sleep(2)
    searchInputText.click()
    searchInputText.send_keys(contactName)
    time.sleep(5)

    contactElement = getContactElement(browser)
    contactElement.click()
    time.sleep(5)

    logging.basicConfig(filename='chat.log', filemode='w', format='%(message)s', level=logging.INFO)
    logDataList = []
    countScrolls = 0

    folderContact = os.path.abspath(os.getcwd()) + '/download/' + contactName

    if os.path.isdir(folderContact) == False:
        os.mkdir(folderContact)

    list_of_files = glob.glob(folderContact + '/*')
    for file in list_of_files:
        print(file)
        os.remove(file)

    while(1):
        iterations = 0
        firstWebElement = []
        flagImg = False
        flagUrl = False
        flagPDF = False

        chatBox = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]')
        allChildrenChatBox = chatBox.find_elements_by_xpath(".//*")

        auxLogDataList = []
        for children in allChildrenChatBox:
            #salva primeiro elemento web pra depois se mover na direção dele
            if iterations < 10:
                firstWebElement.append(children)
            iterations += 1

            print(type(children))
            try:
                print(children.tag_name)
            except StaleElementReferenceException:
                continue
            print(getText(children))

            #mensagem de texto
            if children.tag_name == 'div':
                if children.get_attribute("data-pre-plain-text") is not None and children.get_attribute("data-pre-plain-text") is not '':
                    #adicionando dia, hora e nome do contato
                    d = extractContactData(children.get_attribute("data-pre-plain-text"))

                    print("criterio de parada:", d['day'], d['month'], d['year'])
                    #verifica se programa chegou na data limite
                    if checkStoppingCriterion(d['day'], d['month'], d['year'], thresholdDay, thresholdMonth, thresholdYear) == True:
                        print(logDataList, auxLogDataList)
                        return

                    auxChildren = children.find_elements_by_xpath(".//*")
                    for child in auxChildren:
                        #adicionando a mensagem de texto mesmo
                        if child.tag_name == 'span':
                            #span com mensagem a ser salva não costuma ter atributo algum
                            if checkIfIsSpanWithoutAttributes(child):
                                #pra pegar o ultimo span sem filho, que é a mensagem mesmo
                                if '<' not in getText(child) and '>' not in getText(child) and len(getText(child)) > 0:
                                    d['msg'] = getText(child)
                                    if countScrolls == 0 and d not in logDataList:
                                        addElementInList(logDataList, d)
                                    elif d not in auxLogDataList and d not in logDataList:
                                        addElementInList(auxLogDataList, d)
                                #texto com emoji
                                elif '<img' in getText(child) and 'emoji' in getText(child):
                                    auxChild = child.find_elements_by_xpath(".//*")
                                    for grandChild in auxChild:
                                        if grandChild.tag_name == 'img' and 'emoji' in grandChild.get_attribute('class'):
                                            d['msg'] = getText(child)[:getText(child).find('<')] + " (EMOJI)"
                                            if countScrolls == 0 and d not in logDataList:
                                                addElementInList(logDataList, d)
                                            elif d not in auxLogDataList and d not in logDataList:
                                                addElementInList(auxLogDataList, d)

                        elif child.tag_name == 'img':
                            #é emoji
                            if child.get_attribute("data-plain-text") is not None and 'msg' not in d:
                                d['msg'] = '(EMOJI)'
                            if countScrolls == 0 and d not in logDataList:
                                addElementInList(logDataList, d)
                            elif d not in auxLogDataList and d not in logDataList:
                                addElementInList(auxLogDataList, d)

            #somente a imagem
            if children.tag_name == 'img' and 'blob:' in children.get_attribute("src"):
                #pra ignorar sticker
                if children.get_attribute("draggable") == 'true':
                    children.click()
                    time.sleep(5)

                    downloadElement = getElement(browser, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[4]/div')
                    downloadElement.click()
                    time.sleep(5)

                    quitElement = getElement(browser, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[5]/div')
                    quitElement.click()
                    time.sleep(5)

                    d = {}
                    removeDuplicates(folderContact)

                    d['img'] = getMostRecentFileInDownloadsFolder(folderContact)
                    flagImg = True

                    #verifica se é pdf mesmo
                    extension = d['img'][d['img'].rfind('.'):]
                    print('aaa', children.get_attribute("src"))
                    input()

            #se adicionou uma imagem, precisa então pegar o horário de envio
            if flagImg == True:
                if children.tag_name == 'span' or children.tag_name == 'div':
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        if re.match('[0-9][0-9]:[0-9][0-9]', getText(children)):
                            d['hour'], d['minute'] = getText(children).split(':')
                            if countScrolls == 0 and d not in logDataList:
                                addElementInList(logDataList, d)
                            elif d not in auxLogDataList and d not in logDataList:
                                addElementInList(auxLogDataList, d)
                            flagImg = False

            if children.tag_name == 'a':
                #procurando pdf para baixar
                if children.get_attribute("href") is not None and children.get_attribute("href") is not '':
                    if children.get_attribute("href") == 'https://web.whatsapp.com/#' and '.pdf' in children.get_attribute("title"):
                        children.click()
                        time.sleep(5)

                        d = {}
                        removeDuplicates(folderContact)
                        d['pdf'] = getMostRecentFileInDownloadsFolder(folderContact)

                        #verifica se é pdf mesmo
                        extension = d['pdf'][d['pdf'].rfind('.'):]
                        if extension == '.pdf':
                            flagPDF = True
                    else:
                        #quando a mensagem é só um link
                        d = {}
                        d['msg'] = children.get_attribute("href")
                        flagUrl = True

            #se adicionou uma url, precisa então pegar o horário de envio
            if flagUrl == True:
                if children.tag_name == 'span' or children.tag_name == 'div':
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        if re.match('[0-9][0-9]:[0-9][0-9]', getText(children)):
                            d['hour'], d['minute'] = getText(children).split(':')
                            if countScrolls == 0 and d not in logDataList:
                                addElementInList(logDataList, d)
                            elif d not in auxLogDataList and d not in logDataList:
                                addElementInList(auxLogDataList, d)
                            flagUrl = False
            #se adicionou um pdf, precisa então pegar o horário de envio
            if flagPDF == True:
                if children.tag_name == 'span' or children.tag_name == 'div':
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        if re.match('[0-9][0-9]:[0-9][0-9]', getText(children)):
                            d['hour'], d['minute'] = getText(children).split(':')
                            if countScrolls == 0 and d not in logDataList:
                                addElementInList(logDataList, d)
                            elif d not in auxLogDataList and d not in logDataList:
                                addElementInList(auxLogDataList, d)
                            flagPDF = False
                            print(countScrolls, iterations)

            if countScrolls == 0:
                print(logDataList)
            else:
                print(auxLogDataList)

            print(iterations)
            '''
            if countScrolls > 1 and iterations >= 306:
                input()
            '''

        #rolar pro topo
        if countScrolls > 0:
            logDataList = auxLogDataList + logDataList
            auxLogDataList = []

        scrollToTopElement(firstWebElement, 0)
        countScrolls += 1
        time.sleep(5)
