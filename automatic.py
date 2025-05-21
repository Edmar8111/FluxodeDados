from time import sleep
import pyautogui as pt
import flet as ft
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import testPandas

#return value from xlsx archive
class requestXLSX:
    def __init__(self, list):
        self.list=[]
        fileRead=pd.read_excel('Controle Contábil Geral 2025 - 13.02.2025.xlsx')
        listCIDADE=[a for a in fileRead['Municipio - Estado']]
        listCNPJ=[a for a in fileRead['CNPJ/CPF/CAEPF']]
        for a in range(len(listCIDADE)):
            if listCIDADE[a]=='CUIABÁ-MT':
                self.list.append(listCNPJ[a])
        return None
    def returnList(self, endpoint):
        return self.list
        



def scriptExecute(scriptIn, driver):
    driver.execute_script(scriptIn)
    return

def openNavegator(e):
    global lista
    # efetua a execução e requisição do site
    driver = webdriver.Chrome()
    driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
    driver.execute_script("if(document.querySelector('div.form-group').children[0].innerHTML=='CPF'){document.querySelector('a.btn-block').click()}")
    sleep(0.5)
    pt.press('enter')
    sleep(0.5)
    allInfo=driver.find_elements(By.CSS_SELECTOR, 'ItemStyleNovo, td')
    for a in range(len(allInfo)):
        lista.append(allInfo[a].text)

        #retornar somente cnpj
        if len(allInfo[a].text)==18:
            print(allInfo[a].text)
    sleep(5)
    driver.quit()
    return lista
    # executa a listagem de todos os cnpjs
    # test=driver.execute_async_script
    # lista.append(test('for(a=0;a<document.querySelectorAll("tr.ItemStyleNovo").length;a++){console.log(document.querySelectorAll("tr.ItemStyleNovo")[a].children[1].innerHTML)}'))
    
    #retorna o valor do titulo na aba
    
    
    #Formas de executar o script no pageSource
    textBox=driver.execute_async_script
    #textBox("document.querySelector('a.gb_X').innerHTML=''")
    
    
    
    #buttonSearch.send_keys(Keys.RETURN)
    #assert "Gmail" in driver.page_source

def execAutomatic(e):
    lenPrev=0
    driver = webdriver.Chrome()
    #executa a requisição do site com um certificado/alterar verify
    driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
    driver.execute_script("if(document.querySelector('div.form-group').children[0].innerHTML=='CPF'){document.querySelector('a.btn-block').click()}")
    sleep(1)
    pt.press('enter')
    sleep(1)
    #executa a filtragem dos dados verify page select
    listaV=apiModule=testPandas.request.getFile('')
    execScript=driver.find_element(By.ID, 'TxtCPF')
    execScript.send_keys(f'{listaV[1]}')
    sleep(1)
    execScript0=driver.find_elements(By.CLASS_NAME, "btn.btn-xs.btn-info")
    execScript0[1].click()
    sleep(1)
    sleep(5)
    scriptExec0=driver.execute_script("""
    function test(){
        valueIndex=document.querySelector('#iframe').contentWindow.document.querySelector('select.form-control')
        document.querySelector('#iframe').contentWindow.document.querySelector('select.form-control').selectedIndex=1
        valueIndex.dispatchEvent(new Event('change'))

        setTimeout(function(){
                    document.querySelector('#iframe').contentWindow.document.querySelector('a.btn.btn-xs.btn-success.pull-right').click();
                    if(document.querySelector('a.btn.btn-xs.btn-success.pull-right')){
                        console.log('request')
                    }
                    },10000)                  
        return console.log(valueIndex.selectedIndex)
    }                                  
    function requestTec(valueIn){
        
        if(document.querySelectorAll('a.rtIn')[valueIn].innerHTML=='Emissão de Guia'){
            document.querySelectorAll('a.rtIn')[valueIn].click();
            setTimeout(test,2000)                              
            } 
        }; 
    for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){ requestTec(a) };""")
    sleep(5)
    pt.press('tab')
    sleep(1)
    pt.press('enter')
    sleep(5)
    d=driver.execute_script("document.querySelector('a#ibFechamento').click()")
    sleep(10)
    
    #driver.execute_script("document.querySelectorAll('a.dropdown-toggle')[1].click()")
    
    
    sleep(5)

    driver.quit()
    return

def mainFletApp(page:ft.Page):
    page.theme_mode=ft.ThemeMode.LIGHT
    page.title='App Title'
    page.vertical_alignment=ft.MainAxisAlignment.CENTER
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER
    lista=[]
    buttonExec=ft.ElevatedButton(text='Execute', on_click=execAutomatic)
    def requestInfo():
        global lista
        lista=[]
        # efetua a execução e requisição do site
        chrome_options=Options()
        chrome_options.set_capability('goog:loggingPrefs',{'browser':'ALL'})
        driver = webdriver.Chrome(options=chrome_options)

        driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
        sleep(1)
        driver.execute_script("if(document.querySelector('div.form-group').children[0].innerHTML=='CPF'){document.querySelector('a.btn-block').click()}")
        sleep(1)
        pt.press('enter')
        sleep(0.5)
        infoByPlan=requestXLSX(list())
        returnTrue=0
        #testPandas.request.getFile('')
        for a in infoByPlan.returnList(''):
            sleep(0.5)
            driver.execute_script("document.querySelector('input#TxtCPF.form-control').value=''")
            inputEnter=driver.find_element(By.ID, 'TxtCPF')
            inputEnter.send_keys(f'{a}')
            sleep(1)
            driver.execute_script("document.querySelector('a#imbLocalizar').click()")
            sleep(1.5)
            
            returnTrue=0
            try:
                WebDriverWait(driver, 10).until(EC.title_is('ISSNet On-Line - Nota Eletrônica'))
            except TimeoutException:
                returnTrue+=1
            if driver.title!='Empresas': 
                driver.execute_script("console.log(document.querySelector('span#lblNomeEmpresa').innerHTML)")
                sleep(1)
            else:
                driver.execute_script("console.log('error')")
            log=driver.get_log('browser')

            dictLog=log[-1]
            initText=dictLog['message'].find('"')
            dictLog=dictLog['message'][initText+1:len(dictLog['message'])-1]
            if dictLog!='error':
                lista.append(dictLog)
                lista.append(a)
            else:
                print('valor not found')
                pt.press('tab')
                sleep(1)
                pt.press('enter')
                returnTrue+=1
                pass
            print(dictLog)
            if returnTrue==0:
                driver.execute_script("document.querySelectorAll('a.dropdown-toggle')[1].click()")
                sleep(1)
        #request colum site
        allInfo=driver.find_elements(By.CLASS_NAME, 'ItemStyleNovo')
        
        # for a in range(len(allInfo)):
        #     lista.append(ft.Text(allInfo[a].text))
        sleep(1)
        
        driver.quit()
        
        return lista
    
    def requestEmitir(e):
        driver = webdriver.Chrome()
        driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
        sleep(1)
        driver.execute_script("document.querySelector('a#btnAcionaCertificado').click()")
        sleep(1)
        pt.press('enter')
        sleep(1)
        inputEnter=driver.find_element(By.ID, 'TxtCPF')
        inputEnter.send_keys(f'{e.control.key}')
        print(e.control.key)
        sleep(0.5)
        driver.execute_script("document.querySelector('a#imbLocalizar').click()")
        sleep(1.5)
        if driver.title!='Empresas':
            # return content driver.switch_to.default_content()
            driver.execute_script("""
                                  function verifyNote(counter){
                                    if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Emissão de Guia'){
                                        document.querySelectorAll('a.rtIn')[counter].click();
                                        setTimeout(function(){
                                            document.querySelector('#iframe').contentWindow.document.querySelector('select.form-control').selectedIndex=1; 
                                            document.querySelector('#iframe').contentWindow.document.querySelector('select.form-control').dispatchEvent(new Event('change'))
                                        },1000)
                                    } 
                                  };  
                                  
                                  for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
                                  
                                  """)
            sleep(1)
            driver.execute_script("console.clear(); if(document.querySelector('iframe#iframe').contentWindow.document.querySelector('body').className==''){console.log(true)}else{false}")
            sleep(5)
            log=driver.get_log('browser')
            print(log)
            try:
                driver.find_element(By.ID, 'ibFechamento').click()
            except:
                pass
            sleep(1)
            
        sleep(10)
        driver.quit()
        return 
    
    
    lista=requestInfo()
    
    #First row
    colunaInfo=ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH  # (opcional) Alinha a coluna no centro vertical da tela
    )
    colunaInfo.controls.append(
        ft.Row(controls=[
            ft.Container(ft.Text('RAZÃO SOCIAL', weight=ft.FontWeight.BOLD), alignment=ft.alignment.center, width=400,bgcolor='#BBBBBB',border_radius=5),
            ft.Container(ft.Text('CNPJ',weight=ft.FontWeight.BOLD), alignment=ft.alignment.center, width=400,bgcolor='#BBBBBB',border_radius=5),
            ft.Container(ft.Text('EMISSÃO',weight=ft.FontWeight.BOLD), alignment=ft.alignment.center, width=400,bgcolor='#BBBBBB',border_radius=5)
        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
    )
    
    print(lista)
    while len(lista)>0:
        
        valorIndex=0
        valorA=1
        #valores = infoEmp.value.split()
        # for a in valores:
        #     if len(a)==18:
        #         valorIndex=valores.index(a)
        # #recadastro
        
        #valores[len(valores)-1]
        #Status
        #valores[len(valores)-2]
        #Insc. Municipal
        #valores[len(valores)-3]
            #cnpj
            #valores[len(valores)-4]
            #nome
            #' '.join(valores[0:valorIndex])
            #nameRefined=' '.join(valores[0:valorIndex])
            #spaceAlign=''
            #while len(nameRefined)>50:
            #   spaceAlign=spaceAlign+' '
            
        colunaInfo.controls.append(
            ft.Row(
            controls=[
                
                ft.Container(ft.Text(lista[1]), alignment=ft.alignment.center, width=400,bgcolor='#D9DAD9',border_radius=5),
                ft.Container(ft.Text(lista[0]), alignment=ft.alignment.center, width=400,bgcolor='#D9DAD9',border_radius=5),
                ft.Container(ft.ElevatedButton(text='CLICK', key=lista[1],on_click=requestEmitir) , alignment=ft.alignment.center, width=400,bgcolor='#D9DAD9',border_radius=5)
                
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        )
        del lista[0]
        sleep(0.5)
        del lista[0]
        print(len(lista))
    sleep(5)
    page.add(ft.Text('Fechamento Empresas', size=100, color=ft.Colors.BLACK, italic=False, bgcolor=ft.Colors.GREEN_100, weight=ft.FontWeight.W_100, selectable=False))
    page.add(
        ft.ElevatedButton(text='Executar Automação', on_click=execAutomatic),
        colunaInfo

    )
    page.update()

    return

def requestMSG(msg):
    return print(msg.control.key)

ft.app(target=mainFletApp)