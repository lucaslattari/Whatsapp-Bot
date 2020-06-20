from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, MoveTargetOutOfBoundsException
from utils import *
import time, re, os, os.path
import datetime, json

def checkStopCriterionByDate(currentDay, currentMonth, currentYear, thresholdDay, thresholdMonth, thresholdYear):
    dateMessage = datetime.date(currentYear, currentMonth, currentDay)
    dateThreshold = datetime.date(thresholdYear, thresholdMonth, thresholdDay)
    if dateMessage <= dateThreshold:
        print(dateMessage)
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

def getSortedRecordsByTime(webElementList):
    return sorted(webElementList, key = lambda x:x[1])


def checkIfIsSpanWithoutAttributes(spanElement):
    if spanElement.get_attribute("class") is None or spanElement.get_attribute("class") is '':
        if spanElement.get_attribute("dir") is None or spanElement.get_attribute("dir") is '':
            return True
    return False

def scrollToTopElement(webElementList):
    sortedRecords = getSortedRecordsByTime(webElementList)

    #print(sortedRecords)
    i = 0
    while(1):
        try:
            print(sortedRecords[i][1])
            sortedRecords[i][0].location_once_scrolled_into_view
            webElementList.clear()
            webElementList.append([sortedRecords[i][0], sortedRecords[i][1]])
            return
        except (StaleElementReferenceException, NoSuchElementException) as e:
            i += 1

def accessContactDiv(browser, contactName):
    contactElement = getElement(browser, '/html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/div/div')
    contactElementChildren = contactElement.find_elements_by_xpath(".//*")
    father = None
    for eachElement in contactElementChildren:
        try:
            tagName = eachElement.tag_name
        except (StaleElementReferenceException, NoSuchElementException) as e:
            continue
        if tagName == 'span':
            if eachElement.get_attribute('title') == contactName:
                #achou o span, falta achar a div
                for i in range(0, 100):
                    if i == 0:
                        probableFather = getElement(browser, '/html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/div/div/div')
                    else:
                        probableFather = getElement(browser, '/html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/div/div/div[' + str(i) + ']')

                    if checkIfIsChildren(probableFather, eachElement) == True:
                        father = probableFather
    father.click()
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

def setDownloadsFolder(downloadsFolder):
    downloadsFolder = os.path.abspath(os.getcwd()) + '/download/'
    if os.path.isdir(downloadsFolder) == False:
        os.mkdir(downloadsFolder)

    return downloadsFolder

def getChildrenWebElementsOfChatMessageDiv(browser):
    chatBox = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]')
    if chatBox is None:
        chatBox = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[2]')
    return chatBox.find_elements_by_xpath(".//*")

def doWebScrapOfContact(browser, contactName, thresholdDate):
    thresholdDay, thresholdMonth, thresholdYear = thresholdDate.split("/")

    searchForContact(browser, contactName)
    accessContactDiv(browser, contactName)
    downloadsFolder = setDownloadsFolder(os.path.abspath(os.getcwd()) + '/download/')

    allVisitedElementsSet = set()
    allVisitedElementsByDateList = []
    logDataList = []
    countScrolls = 0

    while(1):
        iterations = 0
        flagImg = False
        flagUrl = False
        flagPDF = False
        finished = True
        auxLogDataList = []
        elementAlbum = None

        allChildrenChatBox = getChildrenWebElementsOfChatMessageDiv(browser)
        for children in allChildrenChatBox:
            #se já tiver visitado
            if children in allVisitedElementsSet:
                continue

            allVisitedElementsSet.add(children)
            finished = False
            iterations += 1

            print(type(children))
            try:
                print(children.tag_name)
            except (StaleElementReferenceException, NoSuchElementException) as e:
                continue

            print(getText(children))

            dateTimeTextExtracted = None
            if elementAlbum is not None:
                if checkIfIsChildren(elementAlbum, children) == False:
                    elementAlbum = None

            if checkTag(children, 'div'):
                if children.get_attribute('data-id') is not None:
                    if 'album-' in children.get_attribute('data-id'):
                        #album de fotos, pra ignorar por enquanto
                        elementAlbum = children

                if children.get_attribute("data-pre-plain-text") is not None and children.get_attribute("data-pre-plain-text") is not '':
                    #mensagem de texto
                    #adicionando dia, hora e nome do contato
                    dateTimeTextExtracted = extractContactData(children.get_attribute("data-pre-plain-text"))

                    print("criterio de parada:", dateTimeTextExtracted['day'], dateTimeTextExtracted['month'], dateTimeTextExtracted['year'])
                    #verifica se programa chegou na data limite
                    if checkStopCriterionByDate(dateTimeTextExtracted['day'], dateTimeTextExtracted['month'], dateTimeTextExtracted['year'], int(thresholdDay), int(thresholdMonth), int(thresholdYear)) == True:
                        logDataList = auxLogDataList + logDataList
                        print(logDataList)
                        with open(contactName + ".json", 'w', encoding='utf8') as jsonFilePointer:
                            json.dump(logDataList, jsonFilePointer, ensure_ascii=False)

                        searchInputText = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')))
                        searchInputText.click()
                        searchInputText.send_keys(Keys.CONTROL, 'a')
                        searchInputText.send_keys(Keys.BACKSPACE)
                        return

                    auxChildren = children.find_elements_by_xpath(".//*")
                    for child in auxChildren:
                        #adicionando a mensagem de texto mesmo
                        if checkTag(child, 'span'):
                        #if child.tag_name == 'span':
                            #span com mensagem a ser salva não costuma ter atributo algum
                            if checkIfIsSpanWithoutAttributes(child):
                                #pra pegar o ultimo span sem filho, que é a mensagem mesmo
                                if '<' not in getText(child) and '>' not in getText(child) and len(getText(child)) > 0:
                                    dateTimeTextExtracted['msg'] = getText(child)
                                    if countScrolls == 0 and dateTimeTextExtracted not in logDataList:
                                        addElementInList(logDataList, dateTimeTextExtracted)
                                    elif dateTimeTextExtracted not in auxLogDataList and dateTimeTextExtracted not in logDataList:
                                        addElementInList(auxLogDataList, dateTimeTextExtracted)
                                #texto com emoji
                                elif '<img' in getText(child) and 'emoji' in getText(child):
                                    auxChild = child.find_elements_by_xpath(".//*")
                                    for grandChild in auxChild:
                                        if checkTag(grandChild, 'img') and 'emoji' in grandChild.get_attribute('class'):
                                        #if grandChild.tag_name == 'img' and 'emoji' in grandChild.get_attribute('class'):
                                            dateTimeTextExtracted['msg'] = getText(child)[:getText(child).find('<')] + " (EMOJI)"
                                            if countScrolls == 0 and dateTimeTextExtracted not in logDataList:
                                                addElementInList(logDataList, dateTimeTextExtracted)
                                            elif dateTimeTextExtracted not in auxLogDataList and dateTimeTextExtracted not in logDataList:
                                                addElementInList(auxLogDataList, dateTimeTextExtracted)

                        elif checkTag(child, 'img'):
                            #é emoji
                            if child.get_attribute("data-plain-text") is not None and 'msg' not in dateTimeTextExtracted:
                                dateTimeTextExtracted['msg'] = '(EMOJI)'
                            if countScrolls == 0 and dateTimeTextExtracted not in logDataList:
                                addElementInList(logDataList, dateTimeTextExtracted)
                            elif dateTimeTextExtracted not in auxLogDataList and dateTimeTextExtracted not in logDataList:
                                addElementInList(auxLogDataList, dateTimeTextExtracted)

            #extrair somente a imagem
            if checkTag(children, 'img') and 'blob:' in children.get_attribute("src") and dateTimeTextExtracted is None:
                #pra ignorar sticker
                if children.get_attribute("draggable") == 'true' and checkIfIsChildren(elementAlbum, children) == False:
                    try:
                        children.click()
                    except:
                        children.location_once_scrolled_into_view
                        time.sleep(3)
                        children.click()
                    time.sleep(5)

                    downloadElement = getElement(browser, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[4]/div')
                    print(downloadElement)
                    #input()

                    if downloadElement is not None:
                        print(downloadElement.get_attribute('title'))
                        #input()
                        if downloadElement.get_attribute('title') == 'Baixar':
                            downloadElement.click()
                            time.sleep(5)

                            dImg = {}
                            wasRemovedDuplicate = removeDuplicates(downloadsFolder)
                            print(wasRemovedDuplicate)
                            #input()
                            if wasRemovedDuplicate == False:
                                dImg['img'] = getMostRecentFileInDownloadsFolder(downloadsFolder)
                                flagImg = True

                    quitElement = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[5]/div')))
                    quitElement.click()
                    time.sleep(5)

            #se adicionou uma imagem, precisa então pegar o horário de envio
            if flagImg == True:
                if checkTag(children, 'span') or checkTag(children, 'div'):
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        if re.match('[0-9][0-9]:[0-9][0-9]', getText(children)):
                            dImg['hour'], dImg['minute'] = getText(children).split(':')
                            if countScrolls == 0 and dImg not in logDataList:
                                addElementInList(logDataList, dImg)
                            elif dImg not in auxLogDataList and dImg not in logDataList:
                                addElementInList(auxLogDataList, dImg)
                            flagImg = False

            #procurando pdf para baixar ou só link
            if checkTag(children, 'a'):
                if children.get_attribute("href") is not None and children.get_attribute("href") is not '':
                    if children.get_attribute("href") == 'https://web.whatsapp.com/#' and '.pdf' in children.get_attribute("title"):
                        children.click()
                        time.sleep(5)

                        dPdf = {}
                        wasRemovedDuplicate = removeDuplicates(downloadsFolder)
                        if wasRemovedDuplicate == False:
                            dPdf['pdf'] = getMostRecentFileInDownloadsFolder(downloadsFolder)

                            #verifica se é pdf mesmo
                            extension = dPdf['pdf'][dPdf['pdf'].rfind('.'):]
                            if extension == '.pdf':
                                flagPDF = True
                    else:
                        #quando a mensagem é só um link
                        dLink = {}
                        dLink['msg'] = children.get_attribute("href")
                        flagUrl = True

            #se adicionou uma url, precisa então pegar o horário de envio
            if flagUrl == True:
                if checkTag(children, 'span') or checkTag(children, 'div'):
                #if children.tag_name == 'span' or children.tag_name == 'div':
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        if re.match('[0-9][0-9]:[0-9][0-9]', getText(children)):
                            dLink['hour'], dLink['minute'] = getText(children).split(':')
                            if countScrolls == 0 and dLink not in logDataList:
                                addElementInList(logDataList, dLink)
                            elif dLink not in auxLogDataList and dLink not in logDataList:
                                addElementInList(auxLogDataList, dLink)
                            flagUrl = False
            #se adicionou um pdf, precisa então pegar o horário de envio
            if flagPDF == True:
                if checkTag(children, 'span') or checkTag(children, 'div'):
                #if children.tag_name == 'span' or children.tag_name == 'div':
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        if re.match('[0-9][0-9]:[0-9][0-9]', getText(children)):
                            dPdf['hour'], dPdf['minute'] = getText(children).split(':')
                            if countScrolls == 0 and dPdf not in logDataList:
                                addElementInList(logDataList, dPdf)
                            elif dPdf not in auxLogDataList and dPdf not in logDataList:
                                addElementInList(auxLogDataList, dPdf)
                            flagPDF = False
                            print(countScrolls, iterations)

            if countScrolls == 0:
                print(logDataList)
            else:
                print(auxLogDataList)
            print(iterations)

            if dateTimeTextExtracted is not None:
                visitedElement = [children, datetime.datetime(dateTimeTextExtracted['year'], dateTimeTextExtracted['month'], dateTimeTextExtracted['day'], dateTimeTextExtracted['hour'], dateTimeTextExtracted['minute'])]
            else:
                visitedElement = [children,datetime.datetime(2099, 12, 12, 12, 12)]
            allVisitedElementsByDateList.append(visitedElement)

        if finished == True:
            finished = False

            print('testando o scroll')
            input()

            browser.find_elements_by_xpath('/html/body/div[1]/div/div/div[4]').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(1)
            browser.find_elements_by_xpath('/html/body/div[1]/div/div/div[4]').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(2)
            browser.find_elements_by_xpath('/html/body/div[1]/div/div/div[4]').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(3)

            continue

        if countScrolls > 0:
            logDataList = auxLogDataList + logDataList
            auxLogDataList = []

        #rolar pro topo
        scrollToTopElement(allVisitedElementsByDateList)
        countScrolls += 1
        time.sleep(5)
