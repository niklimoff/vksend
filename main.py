import lxml.html
import requests
import urllib
import re
from selenium import webdriver
import io
import time
from os import system
from tkinter import *
from tkinter import scrolledtext
from tkinter.filedialog import *
import xml.etree.ElementTree as xml
import xml.etree.cElementTree as ET
import os
import xml.dom.minidom as minidom
from xml.dom.minidom import parseString
import bs4
from bs4 import BeautifulSoup as soup
import string
import asyncio
import aiohttp
from queue import *
from threading import Thread
from PIL import Image, ImageTk
from urllib.request import urlopen
import html
import html.parser
import globalVars

class VKsend:
    def __init__(self, mUrl=globalVars.mUrl):
        self.m_url = mUrl
        self.session = requests.session()
        self.iterator = 0 #Номер рекущего аккаунта
        self.stop = False  # Флаг остаанова потока
        self.start = False  # Флаг р потоботы потока
        self.spamText = globalVars.spamText
        self.videoEntryGet = globalVars.videoEntryGet
    def stopspam(self,):
        self.stop = True # Останов спама
    def authorization(self, login, password):
        print("authorization")
        self.login = login
        self.password = password

        print("login = ", "'" + login + "'")
        print("password = ", "'" + password + "'")

        self.session = requests.session()
        self.data = self.session.get(globalVars.mUrl, headers=globalVars.headers)
        #self.data = self.session.get(globalVars.url, headers=globalVars.headers)
        self.page = lxml.html.fromstring(self.data.content)

        form_vk = self.page.forms[0]
        form_vk.fields['email'] = self.login
        form_vk.fields['pass'] = self.password

        form_action = form_vk.action
        print('form_action = ', form_action)

        handle = open("login.htm", "wb")
        handle.write(self.data.content)
        handle.close()

        if 'https://' in form_action:
            pass
            '''
            if 'https://login' in form_action:
                form_action = form_action.replace('https://login','https://m')
                print('++  form_action = ', form_action)
            '''
        else:
            # Преобразуем относительную ссылку в абсолютную
            form_action = globalVars.mUrl + form_action
            print('--  form_action = ', form_action)

        self.response = self.session.post(form_action, data=form_vk.form_values())

        globalVars.console.configure(state='normal')
        if ('Выход' in self.response.text) == True:
            print('[+] Успешный логин!')
            globalVars.console.insert('end', '[+] Успешный логин!\r\n')
            globalVars.console.see('end')
            globalVars.console.configure(state='disabled')
            self.auth = True
            return {'result': True, 'response': self.response}
        else:
            print('[-] Логин '+self.login+' не удался!')
            globalVars.console.insert('end', '[-] Логин Логин '+self.login+' не удался!\r\n')
            globalVars.console.see('end')
            globalVars.console.configure(state='disabled')
            self.auth = False
            return {'result': False, 'response': self.response}


    def spam(self, variable):
        self.stop = False
        self.variable = variable
        self.urls = globalVars.urls
        self.data = self.session.get(self.urls[variable])
        find = re.findall(r'(?<=\bclass="new_post_link" href=")[^"\"]+', self.data.text)

        print("spam find = ", find)

        if not(self.spamText or self.videoEntryGet):
            print('[-] Не загружен текст рассылки и/или видео!')
            globalVars.console.configure(state='normal')
            globalVars.console.insert('end', '[-] Не загружен текст рассылки и/или видео!\r\n')
            globalVars.console.see('end')
            globalVars.console.configure(state='disabled')
            globalVars.globalFlag = False
            self.start = False
        else:
            if find:
                self.rUrl = globalVars.mUrl + str(find[0])
                print("spam self.rUrl = ", self.rUrl)
                self.data = self.session.get(self.rUrl)
                self.page = lxml.html.fromstring(self.data.content)
                self.form = self.page.forms[0]
                self.form.fields['message'] = self.spamText #spam_text

        		# Если видео
                if self.videoEntryGet:
                    print("self.videoEntryGet=",self.videoEntryGet)
                    self.addUrl = find[0][1:].split('?')
                    pageWithHash = 'https://m.vk.com/attachments?act=choose_video&target='+self.addUrl[0]+'&from=profile'
                    print("videoEntryGet self.pageWithHash = ", pageWithHash)
                    getPageWithHash = self.session.get(pageWithHash)
                    neededHash = re.findall(r'(?:[<a href="\/attachments]+[^"\"&]+&[^"\"&]+&[^"\"&]+&[object=]+[^"\"&]+&hash=)([^"\"]+)', getPageWithHash.text)
                    print("!needed_hash = ", neededHash)

                    print("self.getPageWithHash.text = ", getPageWithHash.text)
                    print("videoEntryGet neededHash = ", neededHash)
                    self.attachmentUrl = 'https://m.vk.com/attachments?act=add&target='+self.addUrl[0]+'&from=profile&object='+self.videoEntryGet+'&hash='+neededHash[0]
                    self.attachVideo = self.session.get(self.attachmentUrl)
                    # @ + Новая форма с солью
                    self.page = lxml.html.fromstring(self.attachVideo.text)
                    self.form = self.page.forms[0]
                    self.form.fields['message'] = self.spamText
                    # @ + Новая форма с солью
                self.formAction=self.form.action
                if 'https://' in self.formAction:
                     pass
                else:
                    # Преобразуем относительную ссылку в абсолютную
                    self.formAction = globalVars.mUrl+self.formAction
                print("spam self.formAction = ", self.formAction)
                formValues = self.form.form_values()
                print('spam formValues = ', formValues)
                self.response = self.session.post(self.formAction, data=formValues)
                # На этом месте проверяется капча
                print('spam ok ')
                return self.response
            else:
                print('Пропуск ')
                globalVars.console.configure(state='normal')
                globalVars.console.insert('end', '[-] Пропуск '+self.urls[self.variable]+'\r\n')
                globalVars.console.see('end')
                globalVars.console.configure(state='disabled')
                self.variable += 1
                return self.response

    def showCaptchaWindow(self,capAuthResponse):#(self, image, response, variable):
        def send():
            self.page = lxml.html.fromstring(response.content)
            form = self.page.forms[0]
            form.fields['captcha_key'] = self.captchaEntry.get()  # captcha_key
            formAction = form.action
            if 'https://' in formAction:
                pass
            else:
                # Преобразуем относительную ссылку в абсолютную
                formAction = globalVars.mUrl + formAction
            print('отправляем капчу formAction = ', formAction)
            self.response = self.session.post(formAction, data=form.form_values())
            self.top.destroy()
            # На этом месте отправляется капча и переменна позиции ссылки в массиве
            globalVars.session = self.session
            globalVars.variable = self.variable
        image = capAuthResponse['image']
        print("capAuthResponse['image'] = ", capAuthResponse['image'])
        response = capAuthResponse['response']
        #self.variable = variable
        self.top = Toplevel(globalVars.root)
        self.top.title('Ввод капчи')
        self.top.resizable(width=False, height=False)
        self.top.transient(globalVars.root)
        self.top.geometry('300x400')
        self.canvas = Canvas(self.top, width=199, height=199)
        self.image = ImageTk.PhotoImage(image)
        self.captchaText = StringVar()

        self.imageSprite = self.canvas.create_image(100, 100, image=self.image)
        self.canvas.pack()
        self.captchaEntry = Entry(self.top, textvariable=self.captchaText)
        self.captchaEntry.pack()
        self.btn = Button(self.top, text="Отправить", command=send)
        self.btn.pack()
        self.top.grab_set()
        self.top.focus_set()
        self.top.wait_window()

# Получение каптчи
    def getCaptcha(self, response, iterator):
        getC = response.text
        soup = bs4.BeautifulSoup(getC)
        getDoc = soup(getC, 'html.parser') # source of raw html
        getImage = None
        getImages = re.findall(r'(?<=\bimg src=")[^"\"]+', getC)
        print('getCaptcha getImages = ', getImages)
        for item in getImages:
            if 'captcha.php' in item:
            #Картинка капчи найдена
                getImage = item
                print("getCaptcha getImage = ", getImage)
                with self.session.get(globalVars.mUrl + getImage) as resp:
                    imageBytes = resp.content
                    image = Image.open(io.BytesIO(imageBytes))
                    image.save('captcha'+str(iterator)+'.jpg')
                    return({'image':image, 'response':response})
                    # Дальше идет вызов showCaptchaWindow
            else:
                pass
        return ({'image': None, 'response': None})

    def sendToConsolePosting(self, variable=None, urls=globalVars.urls):
        self.variable = variable
        self.urls = urls
        globalVars.console.configure(state='normal')
        globalVars.console.insert('end', '[+] Постинг в группу "' + self.urls[self.variable] + '" [' + str(self.variable + 1) + ' из ' + str(
            len(self.urls)) + ']...\r\n')
        globalVars.console.see('end')
        globalVars.console.configure(state='disabled')

    def loadTextWindow(self):
        # Функция загрузки текста рассылки
        def loadText(Event):
            self.videoEntryWithTrash = re.findall(r'(https:\/\/vk.com\/(video)?\?z=+)(["video"][^"\"]+)(?=%)', self.videoEntry.get())
            print(self.videoEntryWithTrash)
            globalVars.videoEntryGet = self.videoEntryWithTrash[0][2]
            globalVars.spamText = self.textLoadConsole.get('1.0', END)
            self.videoEntryGet = globalVars.videoEntryGet
            self.spamText = self.textLoadConsole.get('1.0', END)
            globalVars.console.configure(state='normal')
            globalVars.console.insert('end', 'Контент успешно загружен.\r\n')
            globalVars.console.see('end')
            globalVars.console.configure(state='disabled')
            print("loadText globalVars.videoEntryGet = ", globalVars.videoEntryGet)
            print("loadText globalVars.spamText = ", globalVars.spamText)
        #self.root = Tk()
        self.loadTextWindow = Toplevel(globalVars.root)
        self.loadTextWindow.resizable(width=False, height=False)
        self.loadTextWindow.title('Данные рассылки')
        self.textLoadConsole = scrolledtext.ScrolledText(
            master=self.loadTextWindow,
            wrap=WORD,
            width=30,
            height=20,
            state='normal'
        )
        self.loadTextWindow.configure(width=300, height=200)
        self.textLoadConsole.grid(row=0, column=0)
        self.loadButton = Button(master=self.loadTextWindow, text="Загрузить", command=lambda: self.loadTextWindow.destroy())
        self.loadButton.grid(row=3, column=0)
        self.videoLabel = Label(self.loadTextWindow, text="Видео:")
        self.videoLabel.grid(row=1, column = 0)
        self.videoEntry = Entry(self.loadTextWindow)
        self.videoEntry.grid(row=2, column=0)
        self.loadButton.bind('<Button-1>', loadText)


    # Загрузка УРЛов
    def loadUrls(self):
        self.f = askopenfilename()
        self.file = open(self.f, "r")
        globalVars.console.configure(state='normal')
        self.fArrT = re.findall(r'(http:\/\/|https:\/\/)?(www.)?(vk\.com|vkontakte\.ru)\/(id(\d{9})|[a-zA-Z0-9_.]+)',
                             str(self.file.read().splitlines()))
        for k in range(len(self.fArrT)):
            self.fArr = self.fArrT[k][0] + self.fArrT[k][2] + '/' + self.fArrT[k][3]
            globalVars.urls.append(self.fArr) # Добавление в массив URLs данных из файла
            globalVars.console.insert('end', 'Загрузка ' + str(self.fArr) + '\r\n')
            globalVars.console.see('end')
        globalVars.console.configure(state='disabled')
        print("globalVars.urls = ", globalVars.urls)
        self.file.close()

    #Чтение файла аккаунтов
    def readAccounts(self):
        accounts = []
        if os.path.isfile('accounts.xml'):
            file = open('accounts.xml', 'r')
            data = file.read()
            file.close()
            self.dom = parseString(data)
            names = str(self.handleTok(self.dom.getElementsByTagName('name'))).strip().split(' ')
            logins = str(self.handleTok(self.dom.getElementsByTagName('login'))).strip().split(' ')
            passwords = str(self.handleTok(self.dom.getElementsByTagName('password'))).strip().split(' ')
            for i in range(len(logins)):
                accounts.append({'name': names[i], 'login': logins[i], 'password': passwords[i]})
        return accounts

    # Окно создания нового аккаунта
    def newAccount(self):
        self.accounts = self.readAccounts()  # Чтение файла аккаунтов
        print('self.accounts=',self.accounts)
        def addAccount(Event):
            print('addAccount()')
            if not (os.path.isfile('accounts.xml')) or (not self.accounts):
                root_ = xml.Element("zSender")
                appt = xml.Element("accounts")
                root_.append(appt)
                name = xml.SubElement(appt, "name")
                name.text = self.addAccountEntryName.get()
                login = xml.SubElement(appt, "login")
                login.text = self.addAccountEntryLogin.get()
                password = xml.SubElement(appt, "password")
                password.text = self.addAccountEntryPassword.get()
                tree = xml.ElementTree(root_)
                tree.write(open("accounts.xml", 'w'), encoding='unicode')
                print('addAccount() create')
                self.accounts.append({'name': self.addAccountEntryName.get(), 'login': self.addAccountEntryLogin.get(),
                                      'password': self.addAccountEntryPassword.get()})
            else:
                root_ = xml.Element("zSender")
                appt_ = xml.Element("accounts")
                root_.append(appt_)

                self.accounts.append({'name': self.addAccountEntryName.get(), 'login': self.addAccountEntryLogin.get(),
                                      'password': self.addAccountEntryPassword.get()})

                for i in range(len(self.accounts)):
                    self.name = xml.SubElement(appt_, "name")
                    self.name.text = self.accounts[i]['name']
                    self.login = xml.SubElement(appt_, "login")
                    self.login.text = self.accounts[i]['login']
                    self.password = xml.SubElement(appt_, "password")
                    self.password.text = self.accounts[i]['password']


                tree = xml.ElementTree(root_)
                tree.write(open("accounts.xml", 'w'), encoding='unicode')
                print('addAccount() append')


            print('self.accounts=', self.accounts)

        #self.root = Tk()
        self.addAccountWindow = Toplevel(globalVars.root)
        self.addAccountWindow.resizable(width=False, height=False)
        self.addAccountWindow.title('Add your account')
        self.addAccountEntryNameLabel = Label(master=self.addAccountWindow, text="Наименование: ")
        self.addAccountEntryNameLabel.grid(row=0, column=0)
        self.addAccountEntryName = Entry(master=self.addAccountWindow)
        self.addAccountEntryName.grid(row=0, column=1)
        self.addAccountEntryLoginLabel = Label(master=self.addAccountWindow, text="Логин:")
        self.addAccountEntryLoginLabel.grid(row=1, column=0)
        self.addAccountEntryLogin = Entry(master=self.addAccountWindow)
        self.addAccountEntryLogin.grid(row=1, column=1)
        self.addAccountEntryPasswordLabel = Label(master=self.addAccountWindow, text="Пароль:")
        self.addAccountEntryPasswordLabel.grid(row=2, column=0)
        self.addAccountEntryPassword = Entry(master=self.addAccountWindow)
        self.addAccountEntryPassword.grid(row=2, column=1)
        self.addAccountModalButtonAdd = Button(master=self.addAccountWindow, text="Создать",
                                              command=lambda: self.addAccountWindow.destroy())
        self.addAccountModalButtonAdd.grid(row=4, column=1, sticky=N+E)
        self.addAccountModalButtonAdd.bind('<Button-1>', addAccount)
        self.addAccountModalButtonCancel = Button(master=self.addAccountWindow, text="Отмена",
                                                 command=lambda: self.addAccountWindow.destroy())
        self.addAccountModalButtonCancel.grid(row=4, column=0, sticky=N+E)
        # Функция создания нового аккаунта и запись в XML
        def addAccount(Event):
            if os.path.isfile('accounts.xml'):
                file = open('accounts.xml', 'r')
                data = file.read()
                file.close()
                self.dom = parseString(data)
                self.v1, self.v2, self.v3, self.v4, self.v5 = [],[],[],[],[]
                self.v1.append(str(self.handleTok(self.dom.getElementsByTagName('zSender'))).strip())
                self.sp1 = self.v1[0].split(' ')
                self.v2.append(str(self.handleTok(self.dom.getElementsByTagName('accounts'))).strip())
                self.sp2 = self.v2[0].split(' ')
                self.v3.append(str(self.handleTok(self.dom.getElementsByTagName('name'))).strip())
                self.sp3 = self.v3[0].split(' ')
                self.v4.append(str(self.handleTok(self.dom.getElementsByTagName('login'))).strip())
                self.sp4 = self.v4[0].split(' ')
                self.v5.append(str(self.handleTok(self.dom.getElementsByTagName('password'))).strip())
                self.sp5 = self.v5[0].split(' ')

            if not(os.path.isfile('accounts.xml')) or not(self.sp1 and self.sp2 and self.sp3 and self.sp4):
                self.root_ = xml.Element("zSender")
                self.appt = xml.Element("accounts")
                self.root_.append(self.appt)
                self.name = xml.SubElement(self.appt, "name")
                self.name.text = self.addAccountEntryName.get()
                self.login = xml.SubElement(self.appt, "login")
                self.login.text = self.addAccountEntryLogin.get()
                self.password = xml.SubElement(self.appt, "password")
                self.password.text = self.addAccountEntryPassword.get()
                self.tree = xml.ElementTree(self.root_)
                self.tree.write(open("accounts.xml", 'w'), encoding='unicode')
            else:
                self.root_ = xml.Element("zSender")
                self.appt_ = xml.Element("accounts")
                self.root_.append(self.appt)

                self.sp3.append(self.addAccountEntryName.get())
                self.sp4.append(self.addAccountEntryLogin.get())
                self.sp5.append(self.addAccountEntryPassword.get())

                for i in range(len(self.sp3)):
                    self.name = xml.SubElement(self.appt, "name")
                    self.name.text = self.sp3[i]
                    self.login = xml.SubElement(self.appt, "login")
                    self.login.text = self.sp4[i]
                    self.password = xml.SubElement(self.appt, "password")
                    self.password.text = self.sp5[i]
                self.tree = xml.ElementTree(self.root_)
                self.tree.write(open("accounts.xml", 'w'), encoding='unicode')

    def getAccountData(self, iterator):
        self.iterator = iterator
        self.accounts = self.readAccounts()  # Чтение файла аккаунтов
        print ("self.accounts = ",self.accounts)
        return (self.accounts[iterator]['login'], self.accounts[iterator]['password'])

    def getText(self, nodelist):
        self.nodelist = nodelist
        self.rc = []
        for self.node in self.nodelist:
            if self.node.nodeType == self.node.TEXT_NODE:
                self.rc.append(self.node.data)
        return ''.join(self.rc)


    def handleTok(self, tokenlist):
        self.tokenlist=tokenlist
        self.texts = ""
        for self.token in self.tokenlist:
            self.texts += " " + self.getText(self.token.childNodes)
        return self.texts

    def senderStart(self, Event):
        # -- Исполняемый код
        def senderStartThread():
            login, password = self.getAccountData(self.iterator)
            print("login = ", "'"+login+"'")
            print("password = ", "'"+password+"'")

            authorizationresult = self.authorization(login,password)

            print('authorizationresult=',authorizationresult)

            handle = open("authorizationresult.htm", 'wb')
            handle.write(authorizationresult['response'].text.encode("utf8"))
            handle.close()

            if 'captcha.php' in authorizationresult['response'].text:
                print('требуется ввод каптчи')
                capAuthResponse = self.getCaptcha(authorizationresult['response'], self.iterator)
                if capAuthResponse['image']:
                    shotACW = self.showCaptchaWindow(capAuthResponse)
            if not (globalVars.urls):
                globalVars.console.configure(state='normal')
                globalVars.console.insert('end', '[-] Не найдено ни одного URL\'а. Пожалуйста, загрузите список групп.\r\n')
                globalVars.console.see('end')
                globalVars.console.configure(state='disabled')
            else:
                if self.auth:
                    j = 0
                    k = -1
                    #Авторизация пройдена
                    for i in range(len(globalVars.urls)):
                        mLimit = 95
                        if self.start == False:
                            break
                        else:
                            while self.start:
                                time.sleep(int(timer.get()))
                                response = self.spam(i)
                                k += 1

                                self.sendToConsolePosting(i)

                                print('gad=', self.accounts)

                                if k >= mLimit:
                                    j += 1
                                    globalVars.console.configure(state='normal')
                                    globalVars.console.insert('end', '[*] Превышен лимит сообщений. Реаутентификация...\r\n')
                                    globalVars.console.see('end')
                                    globalVars.console.configure(state='disabled')
                                    login, password  = self.getAccountData(j)
                                    print('senderStartThread login = ', login)
                                    print('senderStartThread password = ', password)
                                    autorisationDict = self.authorization(login = login, password = password)
                                    authResponse = autorisationDict['response']
                                    authResult = autorisationDict['result']
                                    k = -1
                                    if j >= len(self.accounts):
                                        globalVars.globalFlag == False
                                        globalVars.console.configure(state='normal')
                                        globalVars.console.insert('end', '[-] Больше нет доступных аккаунтов. Завершение.\r\n')
                                        globalVars.console.see('end')
                                        globalVars.console.configure(state='disabled')
                                        break
                                    elif '<img src="/images/deactivated_50.png?ava=1">' in response.text:
                                        globalVars.console.insert('end', '[!]Данная страница заблокирована. Реаутентификация...\r\n')
                                        globalVars.console.see('end')
                                        globalVars.console.configure(state='disabled')
                                        j += 1
                                        login, password  = self.getAccountData(j)
                                        print('senderStartThread login = ', login)
                                        print('senderStartThread password = ', password)
                                        autorisationDict = self.authorization(login = login, password = password)
                                        authResponse = autorisationDict['response']
                                        authResult = autorisationDict['result']
                                if response:
                                    print("senderStartThread response = ", response)
                                    print("senderStartThread self.iterator = ", self.iterator)
                                    capResponse = self.getCaptcha(response, self.iterator)
                                    if capResponse:
                                        if capResponse['image'] == None:
                                            break
                                        else:
                                            showCW = self.showCaptchaWindow(capResponse)
                                    #if authResult:
                                        # авторизация успешна
                                    if 'captcha.php' in capResponse:
                                        capAuthResponse = self.getCaptcha(capResponse, self.iterator)
                                        if capAuthResponse:
                                            shotACW = self.showCaptchaWindow(capAuthResponse)
                                            break
                                    else:
                                        print ('нет капчи')
                                        break
            self.start = False
            globalVars.sendingButton['text'] = "Начать"
        #globalVars.globalFlag = True
        if not self.start:
            self.start = True
            Thread(target=senderStartThread, daemon=True).start()  # Запускаем поток отправки статуса
            globalVars.sendingButton['text'] = "Остановить"
        else:
            globalVars.sendingButton['text'] = "Начать"
            self.start = False

globalVars.root = Tk()
globalVars.root.title('VKsender by Nikita Klimov')
globalVars.root.resizable(width=False, height=False)

mainMenu = Menu(globalVars.root)
globalVars.root.configure(menu=mainMenu, width=600, height=500)
itemFile = Menu(mainMenu)

mainMenu.add_cascade(label="Меню", menu=itemFile)

mainFrame = Frame(
    master=globalVars.root,
    width=520,
    height=220,
)
mainFrame.grid_propagate(False)
mainFrame.grid(row=0, column=0)

globalVars.console = scrolledtext.ScrolledText(
    master=mainFrame,
    wrap=WORD,
    width=70,
    height=12,
    state='disabled'
)

globalVars.console.grid(row=1, column=0)

slaveFrame = Frame(
    master=mainFrame,
    width=420,
    height=20
)

slaveFrame.grid(row=2, column=0)

timer = Entry(master=slaveFrame, justify=CENTER)
timer.insert(0, '5')
timer.grid(row=0, column=0)

timer.configure(width=5)

globalVars.sendingButton = Button(
    master=slaveFrame,
    text="Начать"
)

globalVars.sendingButton.configure(width=20)
globalVars.sendingButton.grid(row=0, column=1)

vksend = VKsend()

itemFile.add_command(label="Загрузить список групп", command=vksend.loadUrls)
itemFile.add_command(label="Загрузить текст рассылки", command=vksend.loadTextWindow)
itemFile.add_command(label="Задать аккаунт", command=vksend.newAccount)
itemFile.add_command(label="Выход", command="exit_app")
globalVars.sendingButton.bind("<Button-1>", vksend.senderStart)

globalVars.root.mainloop()
