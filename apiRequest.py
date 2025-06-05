from flask import Flask, jsonify, request, request, abort, url_for, render_template, send_from_directory
import os
from markupsafe import escape, Markup
import pandas as pd
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pyautogui as pt
from time import sleep
from io import BytesIO, StringIO
import json
import shutil
from datetime import date, timedelta
import calendar



def CreateAndMoveFile(pathDirectory, newFolder, folderFile, fileToFind, nameFile):
    print('requisição function')
    pathDirectoryCreate=os.path.join(pathDirectory, newFolder)
    os.makedirs(pathDirectoryCreate, exist_ok=True)
    sleep(5)
    lastFile=sorted(os.listdir(folderFile), key=lambda f: os.path.getmtime(os.path.join(folderFile, f)), reverse=True)
    try:
        if nameFile in os.listdir(pathDirectoryCreate):
            print('Arquivo já baixado')
            os.remove(os.path.join(folderFile, lastFile[fileToFind]))
        else:
            shutil.move(os.path.join(folderFile, lastFile[fileToFind]), os.path.join(pathDirectoryCreate, nameFile))
            sleep(1)
            print(f'File:{lastFile[fileToFind]} moved and rename sucess')
    except Exception as e:
        print(f'ERROR TO MOVE {e}')
    return

class requestXLSX:
    def __init__(self, lista):
        self.lista=[]
        allCNPJ=pd.read_excel('Controle Contábil Geral 2025 - 13.02.2025.xlsx', sheet_name=2)['CNPJ/CPF/CAEPF']
  
        allCity=pd.read_excel('Controle Contábil Geral 2025 - 13.02.2025.xlsx', sheet_name=2)['Municipio - Estado']
        for a in range(allCNPJ.count()):
            if allCity[a]=='CUIABÁ-MT':
                self.lista.append(allCNPJ[a])
        return None
    def requestFile(self, endpoint):
        return self.lista

try:
    lista=requestXLSX(list()).requestFile('')
    print('Lista requisitada')
except Exception as e:
    lista=[]
    print(f'Error {e}')

def requestUrlLIVRO(driver, argKey):
    print(argKey[:10]+argKey[11:])
    if os.path.isfile(f'arquivosApi/{argKey[:10]+argKey[11:]}/livro{int(date.today().month)-1}.pdf') :
        print('Livro já baixado')
    else:
        driver.execute_script("function requestLivro(valueIndex){if(document.querySelectorAll('a.rtIn')[valueIndex].innerHTML=='Emitir Livro Fiscal' ){document.querySelectorAll('a.rtIn')[valueIndex].click() } }; for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){requestLivro(a)}")
        iframe=driver.find_element(By.ID, 'iframe')
        driver.switch_to.frame(iframe)
        Select(driver.find_element(By.ID, 'ddlTipoDocumento')).select_by_visible_text('Livro Fiscal')
        sleep(1.5)
        driver.find_element(By.ID, 'txtLivroFiscalNumLivro').send_keys('1')
        driver.find_element(By.ID, 'txtLivroFiscalPagInicial').send_keys('1')
        driver.find_element(By.ID, 'txtLivroFiscalDtInicial').send_keys('01/05/2025')
        driver.find_element(By.ID,'txtLivroFiscalDtFinal').send_keys('31/05/2025')
        driver.find_element(By.ID, 'btnGerar').click()
        sleep(5)
        pt.hotkey('ctrl', 's')
        sleep(1)
        pt.press('enter')
        sleep(5)
        pt.hotkey('alt', 'f4')
        sleep(5)
        lastFileDownload=sorted(os.listdir(os.path.abspath('C:/Users/209/downloads')), key=lambda e: os.path.getmtime(os.path.join('C:/Users/209/downloads', e)), reverse=True)
        os.makedirs(os.path.join('arquivosApi', argKey[:10]+argKey[11:]), exist_ok=True)
        sleep(1)
        shutil.move(os.path.join(os.path.abspath('C:/Users/209/downloads'), lastFileDownload[0]), os.path.join(f'arquivosApi/{argKey[:10]+argKey[11:]}', f'livro{int(date.today().month)-1}.pdf'))
        sleep(10)
        print('Arquivo baixado')
    return driver.switch_to.default_content()

def requestUrlNT(driver, argKey):
    if os.path.isfile(f'arquivosApi/{argKey[:10]+argKey[11:]}/NotasT{int(date.today().month)-1}.pdf') or os.path.isfile(f'arquivosApi/{argKey[:10]+argKey[11:]}/NotasT{int(date.today().month)-1}.txt'):
        print('Notas Tomadas já baixado')
    else:
        driver.execute_script("function requestNT(value){if(document.querySelectorAll('a.rtIn')[value].innerHTML=='Consulta de Notas Tomadas' ){document.querySelectorAll('a.rtIn')[value].click()}};  for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){requestNT(a)}")
        sleep(4)
        iframe=driver.find_element(By.ID, 'iframe')
        driver.switch_to.frame(iframe)
        sleep(1)
        Select(driver.find_element(By.ID, 'ddlSerie')).select_by_visible_text('Nota Fiscal de Serviço Eletrônica - NFS-e')
        sleep(1)
        driver.execute_script("document.querySelector('input#txtDtEmissaoIni').value='01/05/2025'")
        driver.execute_script("document.querySelector('input#txtDtEmissaoFim').value='31/05/2025'")
        sleep(1)
        driver.find_element(By.ID, 'btnBuscarNotas').click()
        sleep(1)
        driver.find_element(By.ID, 'btnImprimir').click()
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
            print('return span dialog')
            with open(f'arquivosApi/{argKey[:10]+argKey[11:]}/NotasT{int(date.today().month)-1}.txt', 'w', encoding='utf-8') as f:
                f.write('File not found')
        except:
            sleep(5)
            pt.hotkey('ctrl','s')
            sleep(1)
            pt.press('enter')
            sleep(1)
            pt.hotkey('alt','f4')
            sleep(10)
            lastFileDownload=sorted(os.listdir(os.path.abspath('C:/Users/209/downloads')), key=lambda e: os.path.getmtime(os.path.join('C:/Users/209/downloads', e)), reverse=True)
            sleep(1)
            shutil.move(os.path.join(os.path.abspath('C:/Users/209/downloads'), lastFileDownload[0]), os.path.join(f'arquivosApi/{argKey[:10]+argKey[11:]}', f'NotasT{int(date.today().month)-1}.pdf'))
            sleep(5)
            print('Arquivo Baixado')
    return driver.switch_to.default_content()

def requestUrlNFS(driver, argKey):
    print('request NFS')
    if os.path.isfile(f'arquivosApi/{argKey[:10]+argKey[11:]}/NFS25-{int(date.today().month)-1}_a_26-{int(date.today().month)-1}.zip') or os.path.isfile(f'arquivosApi/{argKey[:10]+argKey[11:]}/NFS{int(date.today().month)-1}.txt') or os.path.isfile(f'arquivosApi/{argKey[:10]+argKey[11:]}/NFS{int(date.today().month)-1}.zip'):
        print('NFS-e já baixado')
    else:
        driver.execute_script("""
                function requestNota(value){
                    if(document.querySelectorAll('a.rtIn')[value].innerHTML=='Consultar Nota Eletrônica'){
                        document.querySelectorAll('a.rtIn')[value].click();
                        setTimeout(function(){
                            document.querySelector('iframe#iframe').contentWindow.document.querySelector('a#imbArrow.btn.btn-xs.btn-info').click();
                            document.querySelector('iframe#iframe').contentWindow.document.querySelector('input#txtDtEmissaoIni.form-control').value='01/05/2025';
                            document.querySelector('iframe#iframe').contentWindow.document.querySelector('input#txtDtEmissaoFim.form-control').value='31/05/2025';
                            document.querySelector('iframe#iframe').contentWindow.document.querySelector('a#btnLocalizar2.btn.btn-info.btn-hover-info').click()
                        },1500)
                        
                    } 
                        
                };    
                for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){requestNota(a)}
            """)
        sleep(1)
        iframe=driver.find_element(By.ID, 'iframe')
        driver.switch_to.frame(iframe)
        sleep(1.5)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-open')))
            sleep(1.5)
            with open(f'arquivosApi/{argKey[:10]+argKey[11:]}/NFS{int(date.today().month)-1}.txt', 'w', encoding='utf-8') as f:
                f.write('File not found')
            print('request ativo')
        except Exception as e:
            print(f'Error: {e}')
            
            #caso haja <=10 notas ativas
            try:
                #requisita a quantidade de dias do mes anterior
                dayInit=1
                dayEnd=0
                firstDayMonth=date.today().replace(day=1)
                countPreviousMonth=(firstDayMonth-timedelta(days=1)).day
                for days in range(countPreviousMonth):
                    if dayEnd<=23:
                        dayEnd=dayEnd+5
                    elif dayEnd>23 and dayEnd<countPreviousMonth:
                        dayEnd+=1
                    else:
                        break
                    #Date Data Inicial:
                    driver.execute_script(f"""
                        document.querySelector('input#txtDtEmissaoIni.form-control').value='{dayInit}/05/2025'; 
                        document.querySelector('input#txtDtEmissaoFim.form-control').value='{dayEnd}/05/2025';
                        document.querySelector('a#btnLocalizar2.btn.btn-info.btn-hover-info').click()""")
                    dayInit=dayEnd

                    sleep(5)
                    clickNota=WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'dgDocumentos__ctl2_btnExportarTodosXml')))
                    clickNota.click()
                    sleep(10)
                    lastFileDownload=sorted(os.listdir(os.path.abspath('C:/Users/209/downloads')), key=lambda e: os.path.getmtime(os.path.join('C:/Users/209/downloads', e)), reverse=True)
                    sleep(0.5)     
                    shutil.move(os.path.join(os.path.abspath('C:/Users/209/downloads'), lastFileDownload[0]), os.path.join(f'arquivosApi/{argKey[:10]+argKey[11:]}', f'NFS{dayInit}-{int(date.today().month)-1}_a_{dayEnd}-{int(date.today().month)-1}.zip'))
                    sleep(5)

                # clickNota=WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'dgDocumentos__ctl2_btnExportarTodosXml')))
                # clickNota.click()
                # sleep(5)
                # lastFileDownload=sorted(os.listdir(os.path.abspath('C:/Users/209/downloads')), key=lambda e: os.path.getmtime(os.path.join('C:/Users/209/downloads', e)), reverse=True)
                # sleep(0.5)     
                # shutil.move(os.path.join(os.path.abspath('C:/Users/209/downloads'), lastFileDownload[0]), os.path.join(f'arquivosApi/{argKey[:10]+argKey[11:]}', f'NFS{int(date.today().month)-1}.zip'))
            #caso possua notas acima de 10, percorrera todas as tags
            except Exception as e:
                print(f'ERROR {e}')
                pass
                
    return driver.switch_to.default_content()

def requestGUIAS(driver, argKey):
    iframe=driver.find_element(By.ID, 'iframe')
    switchGuia=False
    try:
        #script referente a requisição da guia contratados
        if os.path.isfile(os.path.join(f'arquivosApi/{argKey[:10]+argKey[11:]}', f'Contratados-{int(date.today().month)-1}.html')) or os.path.isfile(os.path.join(f'arquivosApi/{argKey[10:]+argKey[11:]}', f'ContratadosDan-{int(date.today().month)-1}.html')):
            print('Guia Contratados já baixado')
        else:
            sleep(1)
            #Select the first value in Serviços contratado
            driver.execute_script("""
                function verifyNote(counter){
                    if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Emissão de Guia'){
                        document.querySelectorAll('a.rtIn')[counter].click();
                    } 
                };  
                
                for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
        
                        """)
            sleep(1)
            driver.switch_to.frame(iframe)
            sleep(1)
            Select(driver.find_element(By.CLASS_NAME, 'form-control')).select_by_visible_text('Serviços Contratados')
            try:
                
                print('Request file contratados')
                sleep(1)
                #button popup click
                try:
                    #se o arquivo já foi gerado ele executa a reemissão
                    clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-info.nc-ok')))
                    clickButton.click()
                    sleep(1)
                    driver.switch_to.default_content()
                    driver.execute_script("""
                        function verifyNote(counter){
                            if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Reemissão de Guia'){
                                document.querySelectorAll('a.rtIn')[counter].click();
                            } 
                        };  
                        
                        for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
                
                        """)
                    sleep(1)
                    driver.switch_to.frame(iframe)
                    try:
                        ReemissaoGuia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibNaoMovimento')))
                    except:
                        ReemissaoGuia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao_ctl3_ibGuia')))
                    print('Requisição nota 1')
                    ReemissaoGuia.click()
                    sleep(5)
                    pt.hotkey('ctrl','s')
                    sleep(2)
                    pt.press('enter')
                    sleep(5)
                    pt.hotkey('alt', 'f4')
                    sleep(5)
                    print('Request move file contratados')
                    CreateAndMoveFile('arquivosApi', argKey[:10]+argKey[11:], 'C:/Users/209/downloads', 1, f'Contratados-{int(date.today().month)-1}.html')
                except:
                    #caso a guia não tenha sido emitida
                    clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-success.nc-ok')))
                    print(f'Request first button {clickButton}')
                    clickButton.click()
                    sleep(5)
                    ibNaoMovimento=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibNaoMovimento')))
                    print('Requisição nota 1')
                    ibNaoMovimento.click()
                    sleep(5)
                    pt.hotkey('ctrl','s')
                    sleep(2)
                    pt.press('enter')
                    sleep(5)
                    pt.hotkey('alt', 'f4')
                    sleep(5)

                
                #Button first guia click
                #driver.find_element(By.ID, 'dgReemissao__ctl3_ibNaoMovimento').click()
                    print('Request move file contratados')
                    CreateAndMoveFile('arquivosApi', argKey[:10]+argKey[11:], 'C:/Users/209/downloads', 1, f'Contratados-{int(date.today().month)-1}.html')
            except Exception as e:
                print('Request bt ibFechamento')
                ibFechamento=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ibFechamento')))
                ibFechamento.click()
                print(f'Button ibFechamento request: {ibFechamento}')
                try:
                    checkBox=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'cbConcordo')))
                    if not checkBox.is_selected():
                        checkBox.click()
                        sleep(1.5)
                        driver.find_element(By.ID, 'btnDocumentos').click()
                        sleep(5)
                        pt.hotkey('ctrl','s')
                        sleep(2)
                        pt.press('enter')
                        sleep(5)
                        pt.hotkey('alt', 'f4')
                        sleep(5)
                        print('Request move file contratados')
                        CreateAndMoveFile('arquivosApi', argKey[:10]+argKey[11:], 'C:/Users/209/downloads', 1, f'ContratadosDan-{int(date.today().month)-1}.html')
                        return
                except:
                    
                    dgReemissao_ctl3_ibGuia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao_ctl3_ibGuia')))
                    
                    dgReemissao__ctl3_ibGuia.click()
                    sleep(5)
                    pt.hotkey('ctrl','s')
                    sleep(2)
                    pt.press('enter')
                    sleep(5)
                    pt.hotkey('alt', 'f4')
                    sleep(5)
                    print('Request move file contratados')
                    CreateAndMoveFile('arquivosApi', argKey[:10]+argKey[11:], 'C:/Users/209/downloads', 1, f'Contratados-{int(date.today().month)-1}.html')
        
        #requisição referente ao serviços prestados
        if os.path.isfile(os.path.join(f'arquivosApi/{argKey[:10]+argKey[11:]}', f'Prestados-{int(date.today().month)-1}.html')) or os.path.isfile(os.path.join(f'arquivosApi/{argKey[:10]+argKey[11:]}', f'PrestadosDan-{int(date.today().month)-1}.html')):
            print('File prestados.html já baixado')
        else:
            driver.execute_script("""
                function verifyNote(counter){
                    if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Emissão de Guia'){
                        document.querySelectorAll('a.rtIn')[counter].click();
                    } 
                };  
                
                for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
        
                        """)
            sleep(1)
            driver.switch_to.frame(iframe)
            Select(driver.find_element(By.ID, 'ddlTipoFechamento')).select_by_index(1)
            try:
                print('Request bt ibFechamento')
                ibFechamento=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ibFechamento')))
                ibFechamento.click()
                print(f'Button ibFechamento request: {ibFechamento}')
                
                # interação com o checkbox 
                checkBox=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'cbConcordo')))
                if not checkBox.is_selected():
                    checkBox.click()
                    sleep(1.5)
                    clickDan=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ibGerarGuia')))
                    clickDan.click()
                    sleep(5)
                    driver.switch_to.default_content()
                    driver.execute_script("""
                        function verifyNote(counter){
                            if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Reemissão de Guia'){
                                document.querySelectorAll('a.rtIn')[counter].click();
                            } 
                        };  
                        
                        for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
        
                    """)
                    sleep(1)
                    driver.switch_to.frame(iframe)

                    #verificar o return do valor se executa o redirecionamento
                    emitirDAM=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'dgReemissao_ctl4_ibGuia')))
                    print(f'Request emissão de DAM{emitirDAM}')
                    emitirDAM.click()
                    sleep(5)
                    pt.hotkey('ctrl','s')
                    sleep(1.5)
                    pt.press('enter')
                    sleep(5)
                    pt.hotkey('alt','f4')
                    sleep(5)
                    CreateAndMoveFile('arquivosApi', argKey[:10]+argKey[11:], 'C:/Users/209/downloads', 1, f'PrestadosDan-{int(date.today().month)-1}.html')        
                    return  
            except:
                print('request pos ibFechamento button')
                #verifica se a guia já foi emitida e executa a reemissão
                sleep(5)
                try:
                    clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-success.nc-ok')))
                    clickButton.click()
                except:
                    clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-info.nc-ok')))
                    clickButton.click()
                    pt.press('f5')
                    driver.switch_to.default_content()
                    print('Request script js')
                    driver.execute_script("""
                        function verifyNote(counter){
                            if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Reemissão de Guia'){
                                document.querySelectorAll('a.rtIn')[counter].click();
                            } 
                        };  
                        
                        for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
        
                    """)
                    sleep(1)
                    print('request funct')
                    driver.switch_to.frame(iframe)
                    ibNaoMovimento=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl4_ibNaoMovimento')))
                    ibNaoMovimento.click()
                    sleep(5)
                    pt.hotkey('ctrl','s')
                    sleep(1.5)
                    pt.press('enter')
                    pt.press(5)
                    pt.hotkey('alt','f4')
                    CreateAndMoveFile('arquivosApi', argKey[:10]+argKey[11:], 'C:/Users/209/downloads', 1, f'Prestados-{int(date.today().month)-1}.html')

            sleep(5)
            try:
                #efetua a verificação do arquivo de serviços prestados para efetuar a reemissão
                driver.switch_to.default_content()
                sleep(1)
                driver.execute_script("""
                    function verifyNote(counter){
                        if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Reemissão de Guia'){
                            document.querySelectorAll('a.rtIn')[counter].click();
                        } 
                    };  
                    
                    for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
            
                """)
                sleep(1)
                driver.switch_to.frame(iframe)
                ibNaoMovimento14=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl4_ibNaoMovimento')))
                print('Request a Prestados file')
                ibNaoMovimento14.click()
                sleep(5)
                pt.hotkey('ctrl','s')
                sleep(2)
                pt.press('enter')
                sleep(5)
                pt.hotkey('alt', 'f4')
                sleep(5)
                print('Request move file prestados 1')
                CreateAndMoveFile('arquivosApi', argKey[:10]+argKey[11:], 'C:/Users/209/downloads', 1, f'Prestados-{int(date.today().month)-1}.html')
            except:
                #caso não tenha sido gerado efetua a geração e emissão
                clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-success.nc-ok')))
                clickButton.click()
                sleep(5)
                ibNaoMovimento14=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl4_ibNaoMovimento')))
                ibNaoMovimento14.click()
                sleep(5)
                pt.hotkey('ctrl','s')
                sleep(2)
                pt.press('enter')
                sleep(5)
                pt.hotkey('alt', 'f4')
                sleep(5)
                print('Request move file prestados 2')
                CreateAndMoveFile('arquivosApi', argKey[:10]+argKey[11:], 'C:/Users/209/downloads', 1, f'Prestados-{int(date.today().month)-1}.html')
    except:
        print('Passando direto')
    sleep(5)
    driver.switch_to.default_content()          
    return

def feedAPI(lista):
    listagem=[{'Ativas':[],'Desativas':[]}]
    driver=webdriver.Chrome()
    driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx')
    driver.maximize_window()
    try:
        clickLogin=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'btnAcionaCertificado')))
        clickLogin.click()
        sleep(1.5)
        pt.press('enter')
        sleep(1.5)
        urlHome=driver.current_url
        for a in lista:
            inputInfo=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'TxtCPF')))
            print(a)
            inputInfo.send_keys(a)
            sleep(1.5)
            driver.execute_script("document.querySelector('a#imbLocalizar').click()")
            try:
                WebDriverWait(driver, 1.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
                listagem[0]['Desativas'].append(a)
                print('Empresa não encontrada')
                sleep(0.5)
                driver.get(urlHome)
            except:
                listagem[0]['Ativas'].append(a)
                print('Empresa encontrada')
                requestGUIAS(driver, a)
                sleep(0.5)
                requestUrlLIVRO(driver, a)
                sleep(0.5)
                requestUrlNT(driver, a)
                sleep(0.5)
                requestUrlNFS(driver, a)
                sleep(0.5)
                driver.get(urlHome)
        
        driver.quit()
        return listagem
    except Exception as e:
        print(f'Error>{e}')


app=Flask(__name__)


@app.route('/api/requirement', methods=['GET', 'POST'])
def requestFiles():
    global lista
    try:
        try:
            if os.path.isfile('arquivosApi/dataJson.json')==True:
                print('Arquivo já criado')
                with open('arquivosApi/dataJson.json', 'r') as file:
                    f=file.read()
                return jsonify(f)
            else:
                lista=feedAPI(lista)    
                f=json.dumps(lista)
                f=FileStorage(
                    stream=BytesIO(f.encode('utf-8')),
                    filename='dataJson.json',
                    content_type='text/json',
                )                    
                f.save(os.path.join(os.path.abspath('arquivosApi'),secure_filename(f.filename) ))
                print('Arquivo criado')
                return jsonify(f)
        except Exception as e:
            return f'Erro ao ler Api {e}'
    except Exception as e:
        print(f'Arquivo já criado {e}')
        return jsonify('Arquivo não encontrado')

@app.route('/arquivosApi/<path:param>/<filename>')
def requestData(param, filename):
    print(os.path.abspath(f'arquivosApi/{param}/{filename}'))
    if os.path.isdir(f'arquivosApi/{param}'):
        dataFile=[v for v in os.listdir(f'arquivosApi/{param}')]
    return send_from_directory(f'arquivosApi/{param}', filename, as_attachment=True)

@app.route('/upload/<filename>')
def requestPOST(filename):
    return '<div>Return api</div>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8000')