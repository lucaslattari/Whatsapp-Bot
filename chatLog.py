from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from utils import *
import time, logging, re, os
import datetime

NOTHING = 0
SCRAP_LINK = 1
CLICK_DOWNLOAD = 2
SCRAP_PDF = 3

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

def getLogOfContact(browser, contactName):
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
    while(1):
        iterations = 0
        firstWebElement = ''
        flagImg = False
        flagUrl = NOTHING

        chatBox = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]')
        allChildrenChatBox = chatBox.find_elements_by_xpath(".//*")

        if countScrolls > 0:
            auxLogDataList = []
        for children in allChildrenChatBox:
            #salva primeiro elemento web pra depois se mover na direção dele
            if iterations == 0:
                firstWebElement = children
            iterations += 1

            print(type(children))
            print(children.tag_name)
            print(getText(children))

            #mensagem de texto
            if children.tag_name == 'div':
                if children.get_attribute("data-pre-plain-text") is not None and children.get_attribute("data-pre-plain-text") is not '':
                    #adicionando dia, hora e nome do contato
                    d = extractContactData(children.get_attribute("data-pre-plain-text"))

                    #critério de parada temporário
                    dateMessage = datetime.date(d['year'], d['month'], d['day'])
                    dateThreshold = datetime.date(2020, 4, 30)
                    if dateMessage <= dateThreshold:
                        return

                    auxChildren = children.find_elements_by_xpath(".//*")
                    for child in auxChildren:
                        #adicionando a mensagem de texto mesmo
                        if child.tag_name == 'span':
                            #span com mensagem a ser salva não costuma ter atributo algum
                            #if countScrolls > 0 and iterations > 60:
                            #    print(grandChild)
                            #    input()

                            if checkIfIsSpanWithoutAttributes(child):
                                #pra pegar o ultimo span sem filho, que é a mensagem mesmo
                                grandChild = child.find_elements_by_xpath(".//*")
                                #if countScrolls > 0 and iterations > 60:
                                #   print(grandChild)
                                #   input()
                                if '<' not in getText(child) and '>' not in getText(child) and len(getText(child)) > 0:
                                    d['msg'] = getText(child)
                                    if countScrolls == 0:
                                        addElementInList(logDataList, d)
                                    elif d not in logDataList:
                                        addElementInList(auxLogDataList, d)
                        elif child.tag_name == 'img':
                            #é emoji
                            if child.get_attribute("data-plain-text") is not None:
                                d['msg'] = child.get_attribute("data-plain-text").encode('utf8')
                                if countScrolls == 0:
                                    addElementInList(logDataList, d)
                                elif d not in logDataList:
                                    addElementInList(auxLogDataList, d)
                            #thumbnail de link
                            else:
                                #por enquanto não faz nada
                                pass

            #somente a imagem
            if children.tag_name == 'img' and 'blob:' in children.get_attribute("src"):
                children.click()
                time.sleep(5)

                downloadElement = getElement(browser, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[4]/div')
                downloadElement.click()
                time.sleep(5)

                quitElement = getElement(browser, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[5]/div')
                quitElement.click()
                time.sleep(5)

                d = {}
                removeDuplicates(os.path.abspath(os.getcwd()) + '\download')
                d['img'] = getMostRecentFileInDownloadsFolder(os.path.abspath(os.getcwd()) + '\download')
                flagImg = True
            #se adicionou uma imagem, precisa então pegar o horário de envio
            if flagImg == True:
                if children.tag_name == 'span' or children.tag_name == 'div':
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        d['hour'], d['minute'] = getText(children).split(':')
                        if countScrolls == 0:
                            addElementInList(logDataList, d)
                        elif d not in logDataList:
                            addElementInList(auxLogDataList, d)
                        flagImg = False

            if children.tag_name == 'a':
                if children.get_attribute("href") is not None and children.get_attribute("href") is not '':
                    print('oi1', children.get_attribute("href"))
                    input()
                    #quando a mensagem é só um link
                    d = {}
                    d['msg'] = children.get_attribute("href")
                    flagUrl = SCRAP_LINK

            #se adicionou uma url, precisa então pegar o horário de envio
            if flagUrl == SCRAP_LINK:
                print('oi2', children.tag_name)
                input()
                if children.tag_name == 'span' or children.tag_name == 'div':
                    print('oi3', getText(children))
                    input()
                    if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                        print('oi4', getText(children))
                        input()
                        if re.match('[0-9][0-9]:[0-9][0-9]', getText(children)):
                            d['hour'], d['minute'] = getText(children).split(':')
                            if countScrolls == 0:
                                addElementInList(logDataList, d)
                            elif d not in logDataList:
                                addElementInList(auxLogDataList, d)
                            flagUrl = NOTHING
            '''
            elif flagUrl == CLICK_DOWNLOAD:
                #print('CLICK_DOWNLOAD')
                #input()
                if 'icon-doc-pdf' in children.get_attribute('class'):
                    #print('CLICK_DOWNLOAD')
                    #input()

                    children.click()
                    time.sleep(5)

                    flagUrl = SCRAP_PDF
                else:
                    flagUrl = NOTHING
            elif flagUrl == SCRAP_PDF:
                #print('SCRAP_PDF')
                #input()
                if '<' not in getText(children) and '>' not in getText(children) and len(getText(children)) > 0:
                    d['msg'] = getText(children)
                    if countScrolls == 0:
                        addElementInList(logDataList, d)
                    elif d not in logDataList:
                        addElementInList(auxLogDataList, d)
                    flagUrl = NOTHING
                    #print('ok')
                    #input()
            '''

            if countScrolls == 0:
                print(logDataList)
            else:
                print(auxLogDataList)

            print(iterations)
            if countScrolls > 1 and iterations >= 60:
                input()
            #if iterations > 49:
            #    input()
        #rolar pro topo
        if countScrolls > 0:
            logDataList = auxLogDataList + logDataList
            auxLogDataList = []
            print(logDataList)
            input()

        firstWebElement.location_once_scrolled_into_view
        countScrolls += 1
        time.sleep(5)

        '''
        for i in range(300, 0, -1):
            boxElement = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]/div[' + str(i) + ']/div/div/div/div[1]')
            if boxElement is not None:
                print(i)

                singleDict = {}
                print(boxElement.get_attribute('innerHTML'))
                contactAndDateData = boxElement.get_attribute("data-pre-plain-text")
                print(contactAndDateData)
                if contactAndDateData is None:
                    fatherElement = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]/div[' + str(i) + ']/div/div[1]/div/div/div[1]')
                    allChildren = fatherElement.find_elements_by_xpath(".//*")
                    for children in allChildren:
                        print(children.tag_name)
                        if children.tag_name == 'img':
                            imgElement = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]/div[' + str(i) + ']/div/div[1]/div/div/div[1]/img')
                            imgElement.click()
                            time.sleep(5)

                            downloadElement = getElement(browser, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[4]/div')
                            downloadElement.click()
                            time.sleep(5)

                            quitElement = getElement(browser, '/html/body/div[1]/div/span[3]/div/div/div[2]/div[1]/div[2]/div/div[5]/div')
                            quitElement.click()
                            time.sleep(5)

                            singleDict["img"] = getText(imgElement)

                if contactAndDateData is not None:
                    logging.info('%d %s', i, contactAndDateData)

                    auxStr = re.search('\[(.+?), (.+?)] (.+?):', contactAndDateData)
                    _time, _date, _name = auxStr.group(1), auxStr.group(2), auxStr.group(3)
                    h, m = _time.split(':')
                    d, M, y = _date.split('/')

                    singleDict["hour"] = int(h)
                    singleDict["minute"] = int(m)
                    singleDict["day"] = int(d)
                    singleDict["month"] = int(M)
                    singleDict["year"] = int(y)
                    singleDict["contact"] = _name

                    dateMessage = datetime.date(int(y), int(M), int(d))
                    dateThreshold = datetime.date(2020, 4, 30)

                    if dateMessage <= dateThreshold:
                        return

                textBoxElement = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]/div[' + str(i) + ']/div/div/div/div[1]/div/span[1]/span')
                if textBoxElement is None:
                    textBoxElement = getElement(browser, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]/div[' + str(i) + ']/div/div/div/div[1]/div/div/span')
                if textBoxElement is not None:
                    print(textBoxElement.get_attribute('innerHTML'))
                    message = getText(textBoxElement)

                    #tratamento por conta dos emoticons do zap zap
                    soup = BeautifulSoup(message, "html.parser")
                    emoticonHTML = soup.findAll('img')
                    if emoticonHTML:
                        message = message.encode('utf8')

                    if "img" in singleDict:
                        print(message)
                        singleDict["h"], singleDict["m"] = message.split(':')
                    else:
                        singleDict["msg"] = message
                    if singleDict not in logDataList:
                        print("add")
                        logDataList.append(singleDict)

                    logging.info('%s', message)
                    print(message)
                    print(logDataList)

                lastValidXPathString = '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div/div[3]/div[' + str(i) + ']/div/div/div/div[1]'
        '''
        #boxElement = getElement(browser, lastValidXPathString)
        #boxElement.location_once_scrolled_into_view
