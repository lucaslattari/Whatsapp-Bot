from contactList import writeContactList
from sendMessage import sendSingleMessage, sendMultipleMessages
from chatLog import doWebScrapOfContact
from utils import connectToBrowser
from argparse import ArgumentParser
import time, os.path
import sys

def executeFirstTime():
    os.system('PATH='+os.getcwd()+';%PATH%')

def parse_args():
    parser = ArgumentParser(description = 'Utiliza um bot que automatiza ações do Whatsapp')
    parser.add_argument('bot_operation', help = 'Ação a ser realizada pelo bot (\'sendmsg\' para enviar mensagem, \'scrap\' para extração de informações)')
    parser.add_argument('-c', dest="contactsFile", required = True, help = 'Arquivo contendo lista de contatos')
    parser.add_argument('-m', dest = 'messagesFile', required = False, help = 'Arquivo contendo lista de mensagens (para sendmsg)')
    parser.add_argument('-d', dest="thresholdDay", help = 'Checar mensagens até essa data (para scrap).')

    arguments = parser.parse_args()

    if arguments.bot_operation == 'sendmsg' or arguments.bot_operation == 'scrap':
        if arguments.bot_operation == 'sendmsg':
            if arguments.messagesFile is None:
                print("ERRO: faltou informar parâmetro -m (arquivo de mensagem txt).")
                print("Pressione qualquer coisa para encerrar...")
                input()
                exit()
        elif arguments.bot_operation == 'scrap':
            if arguments.thresholdDay is None:
                print("ERRO: faltou informar parâmetro -d (data limite de busca).")
                print("Pressione qualquer coisa para encerrar...")
                input()
                exit()
        return arguments
    else:
        print("ERRO:", arguments.bot_operation, 'não é operação válida.\nOpções válidas: sendmsg ou scrap.')
        print("Pressione qualquer coisa para encerrar...")
        input()
        exit()

def main():
    executeFirstTime()
    args = parse_args()

    browser = connectToBrowser("https://web.whatsapp.com/")
    print("Aperte ENTER após estar conectado via QR CODE e com a página do Whatsapp carregada.")
    input()

    if args.bot_operation == 'sendmsg':
        f = open(args.contactsFile, "r", encoding='utf-8')
        contacts = f.read().split(",")
        f.close()

        messages = []
        with open(args.messagesFile, "r", encoding='utf-8') as file:
            for line in file:
                messages.append(line)

        sendMultipleMessages(browser, contacts, messages)
    else:
        f = open(args.contactsFile, "r", encoding='utf-8')
        contacts = f.read().split(",")
        f.close()

        for c in contacts:
            doWebScrapOfContact(browser, c, args.thresholdDay)
    browser.close()

if __name__ == "__main__":
    main()
