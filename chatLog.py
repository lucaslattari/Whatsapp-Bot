from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from utils import *
import time, re, os, os.path
import datetime, json

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
    auxChildren = elementFather.find_elements_by_xpath(".//*")
    for child in auxChildren:
        listChildren.append(child)

    if elementChild in listChildren:
        return True
    else:
        return False

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
    #print('aaa', i)
    try:
        elementArray[i].location_once_scrolled_into_view
    except (StaleElementReferenceException, NoSuchElementException) as e:
        scrollToTopElement(elementArray, i + 1)

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

def getLogOfContact(browser, contactName):
    thresholdDay = 30
    thresholdMonth = 4
    thresholdYear = 2020
    searchInputText = getElementIfExists(browser, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')
    searchInputText.click()
    searchInputText.send_keys(contactName)
    time.sleep(5)

    accessContactDiv(browser, contactName)

    logDataList = []
    countScrolls = 0

    folderContact = os.path.abspath(os.getcwd()) + '/download/'
    if os.path.isdir(folderContact) == False:
        os.mkdir(folderContact)

    allVisitedElements = set()

    while(1):
        iterations = 0
        #anotar os elementos visitados
        visitedWebElementInThisLoop = []
        flagImg = False
        flagUrl = False
        flagPDF = False
        finished = True

        chatBox = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]')
        if chatBox is None:
            chatBox = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[2]')
        allChildrenChatBox = chatBox.find_elements_by_xpath(".//*")

        auxLogDataList = []
        elementAlbum = None
        for children in allChildrenChatBox:
            #se já tiver visitado
            if children in allVisitedElements:
                continue
            finished = False

            #salva primeiro elemento web pra depois se mover na direção dele
            visitedWebElementInThisLoop.append(children)
            allVisitedElements.add(children)
            iterations += 1

            print(type(children))
            try:
                print(children.tag_name)
            except (StaleElementReferenceException, NoSuchElementException) as e:
                continue
            print(getText(children))
            dText = None
            if elementAlbum is not None:
                if checkIfIsChildren(elementAlbum, children) == False:
                    elementAlbum = None

            if checkTag(children, 'div'):
            #if children.tag_name == 'div':
                if children.get_attribute('data-id') is not None:
                    if 'album-' in children.get_attribute('data-id'):
                        #album de fotos, pra ignorar por enquanto
                        elementAlbum = children

                if children.get_attribute("data-pre-plain-text") is not None and children.get_attribute("data-pre-plain-text") is not '':
                    #mensagem de texto
                    #adicionando dia, hora e nome do contato
                    dText = extractContactData(children.get_attribute("data-pre-plain-text"))

                    print("criterio de parada:", dText['day'], dText['month'], dText['year'])
                    #verifica se programa chegou na data limite
                    if checkStoppingCriterion(dText['day'], dText['month'], dText['year'], thresholdDay, thresholdMonth, thresholdYear) == True:
                        logDataList = auxLogDataList + logDataList
                        print(logDataList)
                        with open(contactName + ".json", 'w', encoding='utf8') as jsonFilePointer:
                            json.dump(logDataList, jsonFilePointer, ensure_ascii=False)

                        searchInputText = getElementIfExists(browser, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')
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
                                    dText['msg'] = getText(child)
                                    if countScrolls == 0 and dText not in logDataList:
                                        addElementInList(logDataList, dText)
                                    elif dText not in auxLogDataList and dText not in logDataList:
                                        addElementInList(auxLogDataList, dText)
                                #texto com emoji
                                elif '<img' in getText(child) and 'emoji' in getText(child):
                                    auxChild = child.find_elements_by_xpath(".//*")
                                    for grandChild in auxChild:
                                        if checkTag(grandChild, 'img') and 'emoji' in grandChild.get_attribute('class'):
                                        #if grandChild.tag_name == 'img' and 'emoji' in grandChild.get_attribute('class'):
                                            dText['msg'] = getText(child)[:getText(child).find('<')] + " (EMOJI)"
                                            if countScrolls == 0 and dText not in logDataList:
                                                addElementInList(logDataList, dText)
                                            elif dText not in auxLogDataList and dText not in logDataList:
                                                addElementInList(auxLogDataList, dText)

                        elif checkTag(child, 'img'):
                            #é emoji
                            if child.get_attribute("data-plain-text") is not None and 'msg' not in dText:
                                dText['msg'] = '(EMOJI)'
                            if countScrolls == 0 and dText not in logDataList:
                                addElementInList(logDataList, dText)
                            elif dText not in auxLogDataList and dText not in logDataList:
                                addElementInList(auxLogDataList, dText)

            #somente a imagem
            if checkTag(children, 'img') and 'blob:' in children.get_attribute("src") and dText is None:
                #pra ignorar sticker
                if children.get_attribute("draggable") == 'true' and checkIfIsChildren(elementAlbum, children) == False:
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
                            wasRemovedDuplicate = removeDuplicates(folderContact)
                            print(wasRemovedDuplicate)
                            #input()
                            if wasRemovedDuplicate == False:
                                dImg['img'] = getMostRecentFileInDownloadsFolder(folderContact)
                                flagImg = True

                    quitElement = getElement(browser, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[5]/div')
                    quitElement.click()
                    time.sleep(5)

            #se adicionou uma imagem, precisa então pegar o horário de envio
            if flagImg == True:
                if checkTag(children, 'span') or checkTag(children, 'div'):
                #if children.tag_name == 'span' or children.tag_name == 'div':
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        if re.match('[0-9][0-9]:[0-9][0-9]', getText(children)):
                            dImg['hour'], dImg['minute'] = getText(children).split(':')
                            if countScrolls == 0 and dImg not in logDataList:
                                addElementInList(logDataList, dImg)
                            elif dImg not in auxLogDataList and dImg not in logDataList:
                                addElementInList(auxLogDataList, dImg)
                            flagImg = False

            if checkTag(children, 'a'):
            #if children.tag_name == 'a':
                #procurando pdf para baixar
                if children.get_attribute("href") is not None and children.get_attribute("href") is not '':
                    if children.get_attribute("href") == 'https://web.whatsapp.com/#' and '.pdf' in children.get_attribute("title"):
                        children.click()
                        time.sleep(5)

                        dPdf = {}
                        wasRemovedDuplicate = removeDuplicates(folderContact)
                        if wasRemovedDuplicate == False:
                            dPdf['pdf'] = getMostRecentFileInDownloadsFolder(folderContact)

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

        print("finished:", finished)
        if finished == True:
            logDataList = auxLogDataList + logDataList
            print(logDataList)
            with open(contactName + ".json", 'w', encoding='utf8') as jsonFilePointer:
                json.dump(logDataList, jsonFilePointer, ensure_ascii=False)

            searchInputText = getElementIfExists(browser, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]')
            searchInputText.click()
            searchInputText.send_keys(Keys.CONTROL, 'a')
            searchInputText.send_keys(Keys.BACKSPACE)
            return

        #rolar pro topo
        if countScrolls > 0:
            logDataList = auxLogDataList + logDataList
            auxLogDataList = []

        scrollToTopElement(visitedWebElementInThisLoop, 0)
        countScrolls += 1
        time.sleep(5)
