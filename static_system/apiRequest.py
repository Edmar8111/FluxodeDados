import os
import re
import json
import shutil
import calendar
import pandas as pd
import pyautogui as pt
from time import sleep
import dbInit as db
from selenium import webdriver
from io import BytesIO, StringIO
from datetime import date, timedelta
from markupsafe import escape, Markup
from werkzeug.utils import secure_filename
from selenium.webdriver.common.by import By
from werkzeug.datastructures import FileStorage
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, jsonify, request, request, abort, url_for, render_template, send_from_directory, redirect


def CreateAndMoveFile(pathDirectory, newFolder, folderFile, fileToFind, nameFile):
    os.makedirs(f'arquivosApi/{pathDirectory}', exist_ok=True)
    print('REQUEST MOVE FILES VIA FUNCTION', folderFile)
    pathDirectoryCreate=os.path.join(f'arquivosApi/{pathDirectory}/', f'{newFolder}') 
    os.makedirs(pathDirectoryCreate, exist_ok=True)
    print(os.path.abspath(pathDirectoryCreate)) if os.path.isdir(pathDirectory) else False
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

def verify_company_closed(argKey, indice):
    """
        Verifica a condição das notas atuais do cliente, efetuando a verificação se estão todas constando
        CNPJ(argKey):
            identificação da empresa.
        CONDIÇÕES(indice):
            0=Guia contratados
            1=Guia Prestados
            2=Livro Fiscal
            3=Notas Tomadas
            4=NFS-e
    """
    with open('arquivosApi/companyClosed.json', 'r', encoding='utf-8') as file:
        data_file=json.load(file)
        data_file['identify']=argKey
    match indice:
        case 0:
            data_file['guias'][0]=1
        case 1:
            data_file['guias'][1]=1
        case 2:
            data_file['livro']=1
        case 3:
            data_file['notas']=1
        case 4:
            data_file['nfs']=1
    with open('arquivosApi/companyClosed.json', 'w', encoding='utf-8') as file:
        json.dump(data_file, file, indent=4, ensure_ascii=False)
    
    return

def request_IM(driver, argKey):
    #argKey=re.sub(r'\D','',argKey)
    driver.switch_to.default_content()
    im_company=driver.find_element(By.ID, 'lblCae').text
    try:
        id_request_company=0
        modalidade=''
        for i in db.RequestDB('').getData(f'SELECT * FROM company', request.remote_addr):
            if i['cnpj']==argKey:
                id_request_company=i['id']
                modalidade=i['modalidade']
    except Exception as e:
        print(f'Error to find company! {e}')
    finally:
        if id_request_company!=None and modalidade!='':
            im_company=im_company[17:]
            print(id_request_company)
            db.RequestDB('').requestCommitOtimized('UPDATE company SET im=? WHERE id=?', (im_company, id_request_company))
            print('Inscrição Municipal Alterada!')
            

    return driver.switch_to.frame(driver.find_element(By.ID, 'iframe'))


try:
    lista=[]
    #lista=requestXLSX(list()).requestFile('')
    db_files=db.RequestDB('').getData('SELECT * FROM company', 'Automatic')
    for i in db_files:
        lista.append(i['cnpj'])

    print('Lista requisitada com sucesso')
except Exception as e:
    lista=[]
    print(f'Error {e}')

def requestUrlLIVRO(driver, argKey):
    argKey=re.sub(r'\D','',argKey)
    driver.switch_to.default_content()
    firstDayMonth=date.today().replace(day=1)
    countPreviousMonth=(firstDayMonth-timedelta(days=1)).day
    print(countPreviousMonth)
    if os.path.isfile(f'arquivosApi/{argKey}/livros/Livro Fiscal Serviços Prestados ISSQN-{int(date.today().month)-1}-{date.today().year}.pdf') :
        verify_company_closed(argKey, 2)
        return
    else:
        driver.execute_script("function requestLivro(valueIndex){if(document.querySelectorAll('a.rtIn')[valueIndex].innerHTML=='Emitir Livro Fiscal' ){document.querySelectorAll('a.rtIn')[valueIndex].click() } }; for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){requestLivro(a)}")
        try:
            iframe=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'iframe')))
            driver.switch_to.frame(iframe)
        except:
            try:
                driver.switch_to.frame(driver.find_element(EC.presence_of_element_located((By.ID, 'iframe'))))
            except Exception as e:
                print(f'Error to request livro fiscal {e}')
                return
        finally:
            sleep(1)
            Select(driver.find_element(By.ID, 'ddlTipoDocumento')).select_by_visible_text('Livro Fiscal')
            sleep(1.5)
            driver.find_element(By.ID, 'txtLivroFiscalNumLivro').send_keys('1')
            driver.find_element(By.ID, 'txtLivroFiscalPagInicial').send_keys('1')
            driver.find_element(By.ID, 'txtLivroFiscalDtInicial').send_keys(f'01/0{int(date.today().month)-1}/2025')
            driver.find_element(By.ID,'txtLivroFiscalDtFinal').send_keys(f'{countPreviousMonth}/0{int(date.today().month)-1}/2025')
            driver.find_element(By.ID, 'btnGerar').click()
            sleep(10)
            pt.hotkey('ctrl', 's')
            sleep(1)
            pt.press('enter')
            sleep(5)
            pt.hotkey('alt', 'f4')
            sleep(5)
            lastFileDownload=sorted(os.listdir(os.path.join(os.path.expanduser('~'), 'downloads')), key=lambda e: os.path.getmtime(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'), e)), reverse=True)
            os.makedirs(os.path.join(f'arquivosApi/{argKey}', 'livros'), exist_ok=True)
            sleep(1)
            shutil.move(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'), lastFileDownload[0]), os.path.join(f'arquivosApi/{argKey}/livros', f'Livro Fiscal Serviços Prestados ISSQN-{int(date.today().month)-1}-{date.today().year}.pdf'))
            sleep(10)
            verify_company_closed(argKey, 2)
    return driver.switch_to.default_content()

def requestUrlNT(driver, argKey):
    argKey=re.sub(r'\D','',argKey)
    os.makedirs(f'arquivosApi/{argKey}/notasT', exist_ok=True)
    if os.path.isfile(f'arquivosApi/{argKey}/notasT/Relatório Serviços Tomados ISSQN-{int(date.today().month)-1}-{date.today().year}.pdf') or os.path.isfile(f'arquivosApi/{argKey}/notasT/Relatório Serviços Tomados ISSQN-{int(date.today().month)-1}-{date.today().year}.txt'):
        verify_company_closed(argKey, 3)
        return
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
            sleep(5)
            pt.hotkey('ctrl','s')
            sleep(1)
            pt.press('enter')
            sleep(1)
            pt.hotkey('alt','f4')
            sleep(10)
            lastFileDownload=sorted(os.listdir(os.path.join(os.path.expanduser('~'), 'downloads')), key=lambda e: os.path.getmtime(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'), e)), reverse=True)
            sleep(1)
            shutil.move(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'), lastFileDownload[0]), os.path.join(f'arquivosApi/{argKey}/notasT', f'Relatório Serviços Tomados ISSQN-{int(date.today().month)-1}-{date.today().year}.pdf'))
            sleep(5)
            verify_company_closed(argKey, 3)
            return 
        except:
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
                with open(f'arquivosApi/{argKey}/notasT/Relatório Serviços Tomados ISSQN-{int(date.today().month)-1}-{date.today().year}.txt', 'w', encoding='utf-8') as f:
                    f.write('File not found')
                verify_company_closed(argKey, 3)
                return
            except Exception as e:
                print(f'Error to request notas tomadas {e}')
    return driver.switch_to.default_content()

def requestUrlNFS(driver, argKey):
    argKey=re.sub(r'\D','',argKey)
    driver.switch_to.default_content()
    os.makedirs(f'arquivosApi/{argKey}/nfse', exist_ok=True)
    
    if os.path.isfile(f'arquivosApi/{argKey}/nfse/NFS5-{int(date.today().month)-1}_a_10-{int(date.today().month)-1}.zip') or os.path.isfile(f'arquivosApi/{argKey}/nfse/NFS10-{int(date.today().month)-1}_a_15-{int(date.today().month)-1}.zip') or os.path.isfile(f'arquivosApi/{argKey}/nfse/NFS15-{int(date.today().month)-1}_a_20-{int(date.today().month)-1}.zip') or os.path.isfile(f'arquivosApi/{argKey}/nfse/NFS25-{int(date.today().month)-1}_a_26-{int(date.today().month)-1}.zip') or os.path.isfile(f'arquivosApi/{argKey}/nfse/NFS{int(date.today().month)-1}.txt') or os.path.isfile(f'arquivosApi/{argKey}/nfse/NFS-{int(date.today().month)-1}.zip'):
        #verifica se já consta a NFS do mes vigente anterior
        verify_company_closed(argKey, 4)
        return driver.switch_to.default_content()
    else:
        try:
            firstDayMonth=date.today().replace(day=1)
            countPreviousMonth=(firstDayMonth-timedelta(days=1)).day
            sleep(1)
            driver.switch_to.default_content()

            driver.execute_script("""
                    function requestNota(value){
                        if(document.querySelectorAll('a.rtIn')[value].innerHTML=='Consultar Nota Eletrônica'){
                            document.querySelectorAll('a.rtIn')[value].click();
                        } 
                    };    
                    for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){requestNota(a)}
                """)
            driver.switch_to.frame(driver.find_element(By.ID, 'iframe'))
            sleep(1)
            driver.find_element(By.ID, 'imbArrow').click()
            sleep(1)
            driver.find_element(By.ID, 'txtDtEmissaoIni').send_keys(f'01/0{int(date.today().month)-1}/2025')
            driver.find_element(By.ID, 'txtDtEmissaoFim').send_keys(f'{countPreviousMonth}/0{int(date.today().month)-1}/2025')
            sleep(1)
            driver.find_element(By.ID, 'btnLocalizar2').click()
            sleep(1)
            try:
                #caso haja <=10 notas ativas exportando todas de uma vez
                clickNota=WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'dgDocumentos__ctl2_btnExportarTodosXml')))
                clickNota.click()
                sleep(5)
                lastFileDownload=sorted(os.listdir(os.path.join(os.path.expanduser('~'), 'downloads')), key=lambda e: os.path.getmtime(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'), e)), reverse=True)
                sleep(0.5)     
                shutil.move(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'), lastFileDownload[0]), os.path.join(f'arquivosApi/{argKey}/nfse/', f'NFS-{int(date.today().month)-1}.zip'))
                verify_company_closed(argKey, 4)
                return
            except:
                #caso possua notas acima de 10, percorrera todas as tags
                try:#requisita a quantidade de dias do mes anterior
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
                        sleep(1)
                        #Date Data Inicial:
                        driver.execute_script(f"""
                            document.querySelector('input#txtDtEmissaoIni.form-control').value='{dayInit}/06/2025'; 
                            document.querySelector('input#txtDtEmissaoFim.form-control').value='{dayEnd}/06/2025';
                            document.querySelector('a#btnLocalizar2.btn.btn-info.btn-hover-info').click()""")
                        
                        try:
                            popUp=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-info.nc-ok')))
                            popUp.click()
                            dayInit=dayEnd
                            continue
                        except:
                            pass
                            # driver.execute_script("document.querySelector('iframe#iframe').contentDocument.querySelector('button.btn.btn-info.nc-ok').click()")
                            # continue
                        clickNota=WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'dgDocumentos__ctl2_btnExportarTodosXml')))
                        clickNota.click()
                        sleep(10)
                        lastFileDownload=sorted(os.listdir(os.path.join(os.path.expanduser('~'), 'downloads')), key=lambda e: os.path.getmtime(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'), e)), reverse=True)
                        os.makedirs(os.path.join(f'arquivosApi/{argKey}/','nfse'), exist_ok=True)
                        sleep(0.5)     
                        shutil.move(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'), lastFileDownload[0]), os.path.join(f'arquivosApi/{argKey}/nfse/', f'NFS{dayInit}-{int(date.today().month)-1}_a_{dayEnd}-{int(date.today().month)-1}.zip'))
                        dayInit=dayEnd
                        sleep(5)
                except Exception as e:
                        print(f'Erro ao requisitar NFS {e}')
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-open')))
                        sleep(1.5)
                        with open(f'arquivosApi/{argKey}/nfse/NFS{int(date.today().month)-1}.txt', 'w', encoding='utf-8') as f:
                            f.write('File not found')
                        verify_company_closed(argKey, 4)
                        return
                finally:
                    verify_company_closed(argKey, 4)
                    return 
        except Exception as e:
            print(f'Erro ao retornar a nfs {e}')
            return

def requestGUIAS(driver, argKey):
    argKey=re.sub(r'\D','',argKey)
    iframe=driver.find_element(By.ID, 'iframe')
    #script guia contratados
    
    #script referente a requisição da guia contratados
    if os.path.isfile(os.path.join(f'arquivosApi/{argKey}/guias/', f'Contratados ISSQN-{int(date.today().month)-1}.html')) or os.path.isfile(os.path.join(f'arquivosApi/{argKey}/guias/', f'Declaração Não Movto - Serviços-{int(date.today().month)-1}.html')) or os.path.isfile(os.path.join(f'arquivosApi/{argKey}/guias/', f'Contratados Protocolo ISSQN-{int(date.today().month)-1}.html')):
        verify_company_closed(argKey, 0)
        print('Request')
        pass
    else:
        try:
            sleep(1)
            #Efetua a verificação de primeira emissão Serviços contratados
            driver.execute_script("""
                function verifyNote(counter){
                    if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Emissão de Guia'){
                        document.querySelectorAll('a.rtIn')[counter].click();
                    } 
                };  
                
                for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
        
                        """)
            sleep(1)
            driver.switch_to.frame(driver.find_element(By.ID, 'iframe'))
            sleep(1)
            Select(driver.find_element(By.CLASS_NAME, 'form-control')).select_by_visible_text('Serviços Contratados')
                
            #se o arquivo já foi gerado ele executa a reemissão
            clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-success.nc-ok')))
            clickButton.click()
            sleep(1)
            guia_name=f'Guia Contratados{int(date.today().month)-1}.html'
            try:
                ReemissaoGuia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibNaoMovimento')))
                ReemissaoGuia.click()
                guia_name=f'Declaração Não Movto - Serviços-{int(date.today().month)-1}.html'
            except:
                try:
                    ReemissaoGuia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao_ctl3_ibGuia')))
                    ReemissaoGuia.click()
                    guia_name=f'Contratados ISSQN-{int(date.today().month)-1}.html'
                except Exception as e:
                    print(f'Error to request first guia {e}')
                    pass
            finally:
                if ReemissaoGuia:
                    sleep(5)
                    pt.hotkey('ctrl','s')
                    sleep(2)
                    pt.press('enter')
                    sleep(5)
                    pt.hotkey('alt', 'f4')
                    sleep(5)
                    CreateAndMoveFile(argKey, 'guias', os.path.join(os.path.expanduser('~'), 'downloads'), 1, guia_name)
                    verify_company_closed(argKey, 0)
        except:
            try:
                #caso a guia tenha sido emitida
                clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-info.nc-ok')))
                clickButton.click()
                driver.switch_to.default_content()
                driver.execute_script("""
                    function verifyNote(counter){
                        if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Reemissão de Guia'){
                            document.querySelectorAll('a.rtIn')[counter].click();
                        } 
                    };  
                    
                    for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
            
                            """)
                sleep(5)
                driver.switch_to.frame(iframe)
                #verifica guia de não movimento, guia do DAM, protocolo e referencial de doc. exatamente nesta sequencia
                guia_name=f'Contratados ISSQN-{int(date.today().month)-1}.html'
                try:
                    emissao_guia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibNaoMovimento')))
                    emissao_guia.click()
                    guia_name=f'Declaração Não Movto - Serviços-{int(date.today().month)-1}.html'
                except:
                    try:
                        emissao_guia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibGuia')))
                        emissao_guia.click()
                        guia_name=f'Contratados ISSQN-{int(date.today().month)-1}.html'
                    except:
                        try:
                            emissao_guia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibProtocolo')))
                            emissao_guia.click()
                            guia_name=f'Contratados Protocolo ISSQN-{int(date.today().month)-1}.html'
                        except:
                            try:
                                emissao_guia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibRelDocs')))
                                emissao_guia.click()
                                guia_name=f'Contratados Doc ISSQN-{int(date.today().month)-1}.html'
                            except Exception as e:
                                print(f'Error to request file contratados {e}')
                finally:
                    if emissao_guia:
                        sleep(5)
                        pt.hotkey('ctrl','s')
                        sleep(2)
                        pt.press('enter')
                        sleep(5)
                        pt.hotkey('alt', 'f4')
                        sleep(5)
                        CreateAndMoveFile(f"{argKey}", 'guias', os.path.join(os.path.expanduser('~'), 'downloads'), 1, guia_name)
                        verify_company_closed(argKey, 0)

            #emissão com DAM
            except:
                    try:
                        ibFechamento=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ibFechamento')))
                        ibFechamento.click()
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
                                CreateAndMoveFile(argKey,'guias', os.path.join(os.path.expanduser('~'), 'downloads'), 1, f'Guia DAM ISSQN-{int(date.today().month)-1}.html')
                                verify_company_closed(argKey, 0)
                        except:
                            try:
                                clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-success.nc-ok')))
                                clickButton.click()
                                try:
                                    ibNaoMovimento=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibNaoMovimento')))
                                    ibNaoMovimento.click()
                                    sleep(5)
                                    pt.hotkey('ctrl','s')
                                    sleep(2)
                                    pt.press('enter')
                                    sleep(5)
                                    pt.hotkey('alt', 'f4')
                                    sleep(5)
                                    CreateAndMoveFile(argKey,'guias' ,os.path.join(os.path.expanduser('~'), 'downloads'), 1, f'Declaração Não Movto - Serviços -{int(date.today().month)-1}.html')
                                    verify_company_closed(argKey, 0)
                                except:
                                    try:
                                        ibNaoMovimento=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibProtocolo')))
                                        ibNaoMovimento.click()
                                        sleep(5)
                                        pt.hotkey('ctrl','s')
                                        sleep(2)
                                        pt.press('enter')
                                        sleep(5)
                                        pt.hotkey('alt', 'f4')
                                        sleep(5)
                                        CreateAndMoveFile(argKey,'guias', os.path.join(os.path.expanduser('~'), 'downloads'), 1, f'Contratados Protocolo ISSQN-{int(date.today().month)-1}.html')
                                        
                                    except Exception as e:
                                        print(f'Error to request protocolo e não movimento: {e}')
                                        pass
                            except:
                                try:
                                    clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-info.nc-ok')))
                                    clickButton.click()
                                    driver.switch_to.default_content()
                                    driver.execute_script("""
                                        function verifyNote(counter){
                                            if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Reemissão de Guia'){
                                                document.querySelectorAll('a.rtIn')[counter].click();
                                            } 
                                        };  
                                        
                                        for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
                
                                        """)
                                    driver.switch_to.frame(iframe)
                                    #verifica guia de não movimento, guia do DAM, protocolo e referencial de doc. exatamente nesta sequencia
                                    guia_name=f'Contratados ISSQN-{int(date.today().month)-1}.html'
                                    try:
                                        emissao_guia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibNaoMovimento')))
                                        emissao_guia.click()
                                        guia_name=f'Declaração Não Movto - Serviços-{int(date.today().month)-1}.html'
                                    except:
                                        try:
                                            emissao_guia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibGuia')))
                                            emissao_guia.click()
                                            guia_name=f'Contratados ISSQN-{int(date.today().month)-1}.html'
                                        except:
                                            try:
                                                emissao_guia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibProtocolo')))
                                                emissao_guia.click()
                                                guia_name=f'Contratados Protocolo ISSQN-{int(date.today().month)-1}.html'
                                            except:
                                                try:
                                                    emissao_guia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl3_ibRelDocs')))
                                                    emissao_guia.click()
                                                    guia_name=f'Contratados Doc ISSQN-{int(date.today().month)-1}.html'
                                                except Exception as e:
                                                    print(f'Error to request file contratados {e}')
                                    finally:
                                        if emissao_guia:
                                            sleep(5)
                                            pt.hotkey('ctrl','s')
                                            sleep(2)
                                            pt.press('enter')
                                            sleep(5)
                                            pt.hotkey('alt', 'f4')
                                            sleep(5)
                                            CreateAndMoveFile(f"{argKey}", 'guias', os.path.join(os.path.expanduser('~'), 'downloads'), 1, guia_name)
                                            verify_company_closed(argKey, 0)
                                except Exception as e:
                                    print(f'Error to request first button: {e}')
                                    pass
                    except Exception as e:
                        print(f'Guia não gerada: {e}')
     
    #script guia prestados
    try:
        driver.switch_to.default_content()
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
        Select(driver.find_element(By.ID, 'ddlTipoFechamento')).select_by_visible_text('Serviços Prestados')
        #requisição referente ao serviços prestados
        if os.path.isfile(os.path.join(f'arquivosApi/{argKey}/guias', f'Prestados ISSQN-{int(date.today().month)-1}.html')) or os.path.isfile(os.path.join(f'arquivosApi/{argKey}/guias', f'Declaração Não Movto Pres - Serviços-{int(date.today().month)-1}.html')):
            verify_company_closed(argKey, 1)
            return
        else:
            try:
                #verifica se a guia prestados já foi emitida
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
                guia_name=f'Guia Prestados{int(date.today().month)-1}.html'
                try:
                    ReemissaoGuia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl4_ibNaoMovimento')))
                    ReemissaoGuia.click()
                    guia_name=f'Declaração Não Movto Pres - Serviços-{int(date.today().month)-1}.html'
                except:
                    try:
                        ReemissaoGuia=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao_ctl4_ibGuia')))
                        ReemissaoGuia.click()
                        guia_name=f'Prestados ISSQN-{int(date.today().month)-1}.html'
                    except Exception as e:
                        print(f'Error to request first guia {e}')
                        pass
                finally:
                    if ReemissaoGuia:
                        sleep(5)
                        pt.hotkey('ctrl','s')
                        sleep(2)
                        pt.press('enter')
                        sleep(5)
                        pt.hotkey('alt', 'f4')
                        sleep(5)
                        print('Request move file contratados')
                        CreateAndMoveFile(argKey, 'guias', os.path.join(os.path.expanduser('~'), 'downloads'), 1, guia_name)
                        verify_company_closed(argKey, 1)
            except:
                try:
                    ibFechamento=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ibFechamento')))
                    ibFechamento.click()
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
                        emitirDAM.click()
                        sleep(5)
                        pt.hotkey('ctrl','s')
                        sleep(1.5)
                        pt.press('enter')
                        sleep(5)
                        pt.hotkey('alt','f4')
                        sleep(5)
                        CreateAndMoveFile(argKey,'guias', os.path.join(os.path.expanduser('~'), 'downloads'), 1, f'Prestados ISSQN-{int(date.today().month)-1}.html')
                        verify_company_closed(argKey, 0)        
                        return  
                except:
                    #verifica se a guia já foi emitida e executa a emissão se não se sim reemite TRATAMENTO CASO NÂO EMITA A GUIA NAS PRIMEIRA REQUISIÇÕES
                    sleep(5)
                    try:
                        clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-success.nc-ok')))
                        clickButton.click()
                    except:
                        try:
                            clickButton=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-info.nc-ok')))
                            clickButton.click()
                            driver.switch_to.default_content()
                            driver.execute_script("""
                                function verifyNote(counter){
                                    if(document.querySelectorAll('a.rtIn')[counter].innerHTML=='Reemissão de Guia'){
                                        document.querySelectorAll('a.rtIn')[counter].click();
                                    } 
                                };  
                                
                                for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){verifyNote(a); document.querySelectorAll('a.rtIn')[a].innerHTML}
                
                            """)
                        except Exception as e:
                            print(f'Error to request guia prestados {e}')
                            pass
                    finally:
                        if clickButton:
                            sleep(1)
                            driver.switch_to.frame(iframe)
                            ibNaoMovimento=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dgReemissao__ctl4_ibNaoMovimento')))
                            ibNaoMovimento.click()
                            sleep(5)
                            pt.hotkey('ctrl','s')
                            sleep(1.5)
                            pt.press('enter')
                            pt.press(5)
                            pt.hotkey('alt','f4')
                            CreateAndMoveFile(argKey,'guias', os.path.join(os.path.expanduser('~'), 'downloads'), 1, f'Declaração Não Movto Pres - Serviços-{int(date.today().month)-1}.html')
                            verify_company_closed(argKey, 1)
                            return
    except Exception as e:
        print(f'Passando direto {e}')
        verify_company_closed(argKey, 1)
        return
    sleep(5)
    driver.switch_to.default_content()          
    return

def main(lista):
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
                listagem[0]['Ativas'].append(a)
                print('Request guias')
                requestGUIAS(driver, a)
                sleep(1)
                request_IM(driver,a)
                sleep(0.5)
                print('Request livros fiscais')
                requestUrlLIVRO(driver, a)
                sleep(1)
                print('Request notas tomadas')
                requestUrlNT(driver, a)
                sleep(1)
                print('Request NFS')
                requestUrlNFS(driver, a)
                sleep(1)
                with open('arquivosApi/companyClosed.json', 'r') as file:
                    print(json.load(file))
                driver.get(urlHome)
            except TimeoutException as e:
                print(f'Error de timeout: {e}')
                continue
            except:
                WebDriverWait(driver, 1.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
                listagem[0]['Desativas'].append(a)
                print('Empresa não encontrada')
                sleep(0.5)
                driver.get(urlHome)
                continue
            
        driver.quit()
        return listagem
    except Exception as e:
        print(f'Error>{e}')
        return 

app=Flask(__name__)

@app.route('/api/requirement', methods=['GET', 'POST'])
def requestFiles():
    global lista
    try:
        #efetuar a verificação em loop dos valores do arquivo em json para executar uma comparação direta com as empresas ativas no db
        if os.path.isfile('arquivosApi/dataJson.json'):
            print('Arquivo já criado')
            with open('arquivosApi/dataJson.json', 'r') as file:
                f=file.read()
            return jsonify(f)
        else:
            lista=main(lista)    
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
    


#efetua o traçamento da rota para executar o download
@app.route('/arquivosApi/<path:param>/<filename>')
def requestData(param, filename):
    print(os.path.abspath(f'arquivosApi/{param}/{filename}'))
    if os.path.isdir(f'arquivosApi/{param}'):
        dataFile=[v for v in os.listdir(f'arquivosApi/{param}')]
    return send_from_directory(f'arquivosApi/{param}', filename, as_attachment=True) #o as_attachment é responsavel pela execução do download

@app.route('/upload/<filename>')
def requestPOST(filename):
    return '<div>Return api</div>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8000')