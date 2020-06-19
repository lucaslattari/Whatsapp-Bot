from selenium import webdriver
import os, time, random, pickle, keyboard
import os.path
from utils import *

#essa função precisa ser reescrita, não funciona
def writeContactList(browser, contactListFilename):
    #conectando ao zap zap
    browser = connectToBrowser("https://web.whatsapp.com/")

    #lista de contatos inicialmente vazia
    scrappedContactList = set()

    #necessário para visitar as divs
    divCounter = 0
    divsToVisit = [17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    rangeStep = 0
    iterations = 0
    while(1):
        #sem isso, não consegue achar o próximo div e pode entrar em loop
        if(divCounter > 17):
            divCounter = 0

        #por aqui "pegamos" o elemento lateral em que estão os contatos
        xPathPaneside = "/html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/div/div/div"
        if divCounter > 0:
            xPathPaneside += '[' + str(divCounter) + ']'
        panesideElement = getElement(browser, xPathPaneside)
        if panesideElement is None:
            divCounter += 1
            continue

        #pra saber se podemos continuar o passo de descida
        sizeOfListLastIteration = len(scrappedContactList)

        '''existem variações ao extrair o nome na caixa de texto do
        contato. abaixo temos a primeira variação'''
        xPathContactBox = xPathPaneside + '/div/div/div[2]/div[1]/div[1]/div/span'
        contactElement = getElement(browser, xPathContactBox)
        if contactElement is not None:
            newContactName = getText(contactElement)
            if newContactName != '':
                scrappedContactList.add(newContactName)
        else:
            '''existem variações ao extrair o nome na caixa de texto do
            contato. abaixo temos a segunda variação'''
            xPathContactBox = xPathPaneside + '/div/div/div[2]/div[1]/div[1]/span/span'
            contactElement = getElement(browser, xPathContactBox)
            if contactElement is not None:
                newContactName = getText(contactElement)
                if newContactName != '':
                    scrappedContactList.add(newContactName)

        #se a lista aumentou, o passo volta a diminuir
        if(sizeOfListLastIteration < len(scrappedContactList)):
            rangeStep = 0

        print(rangeStep, len(scrappedContactList))

        #esse trecho faz o mouse se movimentar para baixo
        if contactElement is not None:
            #a ideia é sortear alguma div mais distante para poder "andar"
            neighborDivId = divCounter + rangeStep
            if neighborDivId > 17:
                neighborDivId = neighborDivId % 18
            if divCounter == divsToVisit[neighborDivId]:
                contactElement.location_once_scrolled_into_view
        divCounter += 1
        iterations += 1

        if iterations > 200:
            iterations = iterations % 200
            rangeStep += 1

        if keyboard.is_pressed('q'):
            break

    browser.close()

    #salva em um arquivo em disco essa lista de contatos
    if os.path.exists(contactListFilename):
        contactListFilePointerRead = open(contactListFilename,'rb')
        oldContactList = pickle.load(contactListFilePointerRead)
        contactListFilePointerRead.close()
        print(oldContactList, len(oldContactList))

        finalContactList = scrappedContactList.union(oldContactList)
        print(finalContactList, len(finalContactList))

        contactListFilePointerWrite = open(contactListFilename,'wb')
        pickle.dump(finalContactList, contactListFilePointerWrite)
        contactListFilePointerWrite.close()
    else:
        contactListFilePointerWrite = open(contactListFilename,'wb')
        pickle.dump(scrappedContactList, contactListFilePointerWrite)
        contactListFilePointerWrite.close()
        print(scrappedContactList, len(scrappedContactList))
