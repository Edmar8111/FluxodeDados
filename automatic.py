from time import sleep
import os
import shutil
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

#criar script que retorna valor direto na execução automatica
class requestXLSX:
    def __init__(self, list, pathDirectory):
        self.list=[]
        self.pathDirectory=pathDirectory
        return None
    def returnXLSX(self):
        listXLSX=pd.read_excel(self.pathDirectory)
        listaCIDADE=[a for a in listXLSX['Municipio - Estado']]

        for a in range(len(listaCIDADE)):
            if listaCIDADE[a]=='CUIABÁ-MT':
                self.list.append(listXLSX['CNPJ/CPF/CAEPF'][a])
                self.list.append(listXLSX['Razão Social'][a])
        return self.list

class ExecuteEmissoes:
    def __init__(self, e):
        driver=webdriver.Chrome()
        driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
        sleep(1)
        driver.execute_script("document.querySelector('a#btnAcionaCertificado.btn-block').click()")
        sleep(5)
        pt.press('enter')
        sleep(0.5)
        try:
            while WebDriverWait(driver, 1.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog'))):
                sleep(1.5)
                driver.execute("document.querySelector('button.btn.btn-info.nc-ok').click()")
                sleep(1.5)
                driver.execute_script("document.querySelector('a#btnAcionaCertificado.btn-block').click()")
                sleep(1.5)
                pt.press('enter')
                sleep(1.5)
        except:
            driver.execute_script("document.querySelector('input#TxtCPF.form-control').value=''")
            inputEnter=driver.find_element(By.ID, 'TxtCPF')
            sleep(1)
            inputEnter.send_keys(e.control.data['cnpj'])
            sleep(1)
            driver.execute_script("document.querySelector('a#imbLocalizar').click()")
            sleep(1)
            requestXMLNota(driver, e.control.data['name'])
            sleep(5)
            requestLivro(driver, e.control.data['name'])
            driver.quit()
        return None
    def requestNFS(self, endpoint):
        return

def requestXMLNota(driver, folderName):
        pastaXML=os.path.abspath("xmlFolder")
        driver.execute_script("""
                function requestNota(value){
                    if(document.querySelectorAll('a.rtIn')[value].innerHTML=='Consultar Nota Eletrônica'){
                        document.querySelectorAll('a.rtIn')[value].click();
                        setTimeout(function(){
                            document.querySelector('iframe#iframe').contentWindow.document.querySelector('a#imbArrow.btn.btn-xs.btn-info').click();
                            document.querySelector('iframe#iframe').contentWindow.document.querySelector('input#txtDtEmissaoIni.form-control').value='01/04/2025';
                            document.querySelector('iframe#iframe').contentWindow.document.querySelector('input#txtDtEmissaoFim.form-control').value='30/04/2025';
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
            driver.execute_script("document.querySelector('button.btn.btn-info.nc-ok').click()")
            print('request ativo')
        except TimeoutException as e:
            print(f'Error: {e}')
            try:
                if os.path.isfile(os.path.join(f'C:/Users/209/Desktop/script-code/execBot/xmlFolder/{folderName[:25]}/NFS.zip')):
                    print('Arquivo já baixado')
                else:
                    clickNota=WebDriverWait(driver, 5).until( EC.visibility_of_element_located((By.ID, 'dgDocumentos__ctl2_btnExportarTodosXml'))) 
                    folderCreate=os.path.abspath(f'C:/Users/209/Desktop/script-code/execBot/xmlFolder/{folderName[:25]}')
                    os.makedirs(folderCreate, exist_ok=True)
                    clickNota.click()
                    sleep(5)
                    arquivos=[a for a in os.listdir("C:/Users/209/downloads")]
                    for a in arquivos:
                        if '.zip' in a:
                            shutil.move(f'C:/Users/209/downloads/{a}', os.path.join(folderCreate, 'NFS.zip'))
                            sleep(5)
                            break
                    print('request ativo')
            except TimeoutException:
                print('ERROR nota eletronica not found')
                pass      
            sleep(5)
        sleep(1.5)
            
        return driver.switch_to.default_content()

def CreateAndMoveFile(pathDirectory, newFolder, folderFile, fileToFind, nameFile):
    print('requisição function')
    pathDirectoryCreate=os.path.join(pathDirectory, newFolder)
    os.makedirs(pathDirectoryCreate, exist_ok=True)
    sleep(5)
    lastFile=sorted(os.listdir(folderFile), key=lambda f: os.path.getmtime(os.path.join(folderFile, f)), reverse=True)
    try:
        if nameFile in os.listdir(pathDirectoryCreate):
            print('Arquivo já baixado')
            os.remove(os.path.join(folderFile, lastFile[0]))
        else:
            shutil.move(os.path.join(folderFile, lastFile[0]), os.path.join(pathDirectoryCreate, nameFile))
            sleep(1)
            print('File moved and rename sucess')
    except Exception as e:
        print(f'ERROR TO MOVE {e}')
    return

def emitirNotasTomadas(e):
    driver=webdriver.Chrome()
    driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
    sleep(1)
    driver.execute_script("document.querySelector('a#btnAcionaCertificado.btn-block').click()")
    sleep(1)
    pt.press('enter')
    sleep(1)

    try:
        inputSearch=driver.find_element(By.ID, 'TxtCPF')
        sleep(1.5)
        inputSearch.send_keys(e.control.data['cnpj'])
        sleep(1)
        driver.execute_script("document.querySelector('a#imbLocalizar.btn.btn-xs.btn-info').click()")
        sleep(1)
        driver.execute_script("function requestNT(value){if(document.querySelectorAll('a.rtIn')[value].innerHTML=='Consulta de Notas Tomadas' ){document.querySelectorAll('a.rtIn')[value].click()}};  for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){requestNT(a)}")
        sleep(4)
        iframe=driver.find_element(By.ID, 'iframe')
        driver.switch_to.frame(iframe)
        sleep(1)
        Select(driver.find_element(By.ID, 'ddlSerie')).select_by_visible_text('Nota Fiscal de Serviço Eletrônica - NFS-e')
        sleep(1)
        driver.execute_script("document.querySelector('input#txtDtEmissaoIni').value='01/04/2025'")
        driver.execute_script("document.querySelector('input#txtDtEmissaoFim').value='30/04/2025'")
        sleep(1)
        driver.find_element(By.ID, 'btnBuscarNotas').click()
        sleep(1)
        driver.find_element(By.ID, 'dgDocumentos__ctl2_btnExpPdfTodos').click()
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
            print('return span dialog')
        except:
            sleep(5)
            pt.hotkey('ctrl','s')
            sleep(1)
            pt.press('enter')
            sleep(10)
            CreateAndMoveFile('C:/Users/209/Desktop/script-code/execBot/xmlFolder', e.control.data['name'][:25], 'C:/Users/209/downloads', '', 'NotasTomadas.pdf')
        print('Request exit...')
        sleep(5)
        return driver.quit()
        

    except TimeoutException as e:
        print(f'Error {e}')
        driver.switch_to.default_content()
        return driver.quit()
    driver.quit()
    return

def automaticNT(driver, folderName):
        driver.execute_script("function requestNT(value){if(document.querySelectorAll('a.rtIn')[value].innerHTML=='Consulta de Notas Tomadas' ){document.querySelectorAll('a.rtIn')[value].click()}};  for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){requestNT(a)}")
        sleep(4)
        iframe=driver.find_element(By.ID, 'iframe')
        driver.switch_to.frame(iframe)
        sleep(1)
        Select(driver.find_element(By.ID, 'ddlSerie')).select_by_visible_text('Nota Fiscal de Serviço Eletrônica - NFS-e')
        sleep(1)
        driver.execute_script("document.querySelector('input#txtDtEmissaoIni').value='01/04/2025'")
        driver.execute_script("document.querySelector('input#txtDtEmissaoFim').value='30/04/2025'")
        sleep(1)
        driver.find_element(By.ID, 'btnBuscarNotas').click()
        sleep(1)
        driver.find_element(By.ID, 'dgDocumentos__ctl2_btnExpPdfTodos').click()
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
            print('return span dialog')
        except:
            sleep(5)
            pt.hotkey('ctrl','s')
            sleep(1)
            pt.press('enter')
            sleep(1)
            pt.hotkey('alt','f4')
            sleep(10)
            CreateAndMoveFile('C:/Users/209/Desktop/script-code/execBot/xmlFolder', folderName[:25], 'C:/Users/209/downloads', '', 'NotasTomadas.pdf')
        print('Request exit...')
        driver.switch_to.default_content()
        return 

def requestLivro(driver, folderName):
        #retornar um valor que requisita de forma mais fluida
        driver.execute_script("function requestLivro(valueIndex){if(document.querySelectorAll('a.rtIn')[valueIndex].innerHTML=='Emitir Livro Fiscal' ){document.querySelectorAll('a.rtIn')[valueIndex].click() } }; for(a=0;a<document.querySelectorAll('a.rtIn').length;a++){requestLivro(a)}")
        try:
            iframe=driver.find_element(By.ID, 'iframe')
            driver.switch_to.frame(iframe)
            Select(driver.find_element(By.ID, 'ddlTipoDocumento')).select_by_visible_text('Livro Fiscal')
            sleep(1.5)
            driver.find_element(By.ID, 'txtLivroFiscalNumLivro').send_keys('1')
            driver.find_element(By.ID, 'txtLivroFiscalPagInicial').send_keys('1')
            driver.find_element(By.ID, 'txtLivroFiscalDtInicial').send_keys('01/04/2025')
            driver.find_element(By.ID,'txtLivroFiscalDtFinal').send_keys('30/04/2025')
            driver.find_element(By.ID, 'btnGerar').click()
            sleep(10)
            pt.hotkey('ctrl','s')
            sleep(1)
            pt.press('enter')
            sleep(1)
            pt.hotkey('alt', 'F4')
            # pt.press(['tab','tab','tab','tab','tab','tab','tab','tab','tab','tab','tab','tab','tab','tab','tab','tab','tab','enter'])
            sleep(5)
            print(folderName)
            CreateAndMoveFile('C:/Users/209/Desktop/script-code/execBot/xmlFolder', folderName[:25], 'C:/Users/209/downloads/', 'Relatorio.pdf', 'livro.pdf')
            sleep(10)
            print('requisição de alterção de livro efetuada')
        except:
            pass
     
        return driver.switch_to.default_content()


def execAutomatic(pathFile):
    print(pathFile)
    lenPrev=0
    driver = webdriver.Chrome()
    #executa a requisição do site com um certificado/alterar verify
    driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
    driver.execute_script("if(document.querySelector('div.form-group').children[0].innerHTML=='CPF'){document.querySelector('a.btn-block').click()}")
    sleep(1)
    pt.press('enter')
    sleep(1)
    #executa a filtragem dos dados verify page select
    lista=requestXLSX(list(), pathFile).returnXLSX()
    urlHome=driver.current_url
    while len(lista)>0:
        print(lista[1])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'TxtCPF')))
        driver.execute_script("document.querySelector('input#TxtCPF.form-control').value=''")
        driver.find_element(By.ID, 'TxtCPF').send_keys(lista[0])
        sleep(1)
        driver.find_element(By.ID, 'imbLocalizar').click()
        sleep(1)
        requestLivro(driver, lista[1]) #requisita o livro fiscal
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
            driver.find_element(By.CLASS_NAME, 'btn.btn-info.nc-ok').click
        except:    
            sleep(5)
            requestXMLNota(driver, lista[1]) #requisita as nfs de serviços
            sleep(5)
            automaticNT(driver, lista[1]) # requisica as nfs de serviços tomados
        del lista[0]
        sleep(1)
        del lista[0]
        driver.get(urlHome)
    return driver.quit()


#atribuição de atalhos as funções
def on_keyboardEvent(e: ft.KeyboardEvent):
    print(type(e.key), e.key)
    if e.key=='F1':
        execAutomatic(e)
        return 

def mainFletApp(page:ft.Page):
    #estilização de temas e titulo
    is_dark_mode = ft.Ref[bool]()
    icon_mode = ft.Ref[ft.IconButton]()

    page.theme=ft.Theme(color_scheme_seed=ft.Colors.PINK_100)
    page.title='Tally Automation System'
    #alinhamento
    page.vertical_alignment=ft.MainAxisAlignment.START
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER
    page.on_keyboard_event=on_keyboardEvent
    
    def chooseMode(e):
        is_dark_mode.current=not is_dark_mode.current
        icon_mode.current.icon=(ft.Icons.DARK_MODE if is_dark_mode.current else ft.Icons.LIGHT_MODE)
        page.theme_mode = ft.ThemeMode.DARK if is_dark_mode.current else ft.ThemeMode.LIGHT
        page.update()

        return print(icon_mode.current.icon)
    btn = ft.IconButton(icon=ft.Icons.LIGHT_MODE,ref=icon_mode, icon_size=25,tooltip='Alterar Tema',on_click=chooseMode)
    page.appbar=ft.AppBar(
        leading=ft.Image(src='logo.png', border_radius=ft.border_radius.all(50)),
        leading_width=100,title=ft.Row(controls=[ft.Text('Tolls'), ft.Icon(ft.Icons.TASK_ALT)]),center_title=False,
        actions=[btn],
        bgcolor=ft.Colors.WHITE
    )

    pastaXML=os.path.abspath("xmlFolder")
        # efetua a execução e requisição do site
    chrome_options=Options()
    chrome_options.set_capability('goog:loggingPrefs',{'browser':'ALL'})
    prefs={
        'download.default_directory':pastaXML,
        'download.prompt_for_download':False,
        'download.directory_upgrade':True,
        'safebrowsing.enabled':True
    }
    lista=[]
    pathFile=''
    #lista=requestXLSX(list() )
    #lista=lista.returnXLSX('')
    
    def planilhaIndex(e: ft.FilePickerResultEvent):
        global lista, pathFile
        print(f"Selected files: {str(e.files[0].path)[-4:]}")
        try: 
            if str(e.files[0].path)[-4:]=='xlsx' and 'CNPJ/CPF/CAEPF' in pd.read_excel(e.files[0].path, nrows=0).columns.tolist():
                pathFile=e.files[0].path
                lista=requestXLSX(list(),e.files[0].path).returnXLSX()
                page.remove(listWithFunction[0])
                page.add(listWithFunction[2])
                page.update()
                requestPageEmpresasCB()
            else:
                page.add(listWithFunction[1])
                page.update()
                sleep(5)
                page.remove(listWithFunction[1])
        except Exception as e:
            print(f'Error {e}')
    file_picker=ft.FilePicker(on_result=planilhaIndex)
    page.overlay.append(file_picker)
    

    def requestInfo():
        global lista
        pastaXML=os.path.abspath("xmlFolder")
        # efetua a execução e requisição do site
        chrome_options=Options()
        chrome_options.set_capability('goog:loggingPrefs',{'browser':'ALL'})
        prefs={
            'download.default_directory':pastaXML,
            'download.prompt_for_download':False,
            'download.directory_upgrade':True,
            'safebrowsing.enabled':True
        }
        lista=[]

        driver = webdriver.Chrome(options=chrome_options)

        driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
        sleep(1)
        driver.execute_script("document.querySelector('a#btnAcionaCertificado.btn-block').click()")
        sleep(5)
        pt.press('enter')
        sleep(0.5)
        try:
            while WebDriverWait(driver, 1.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog'))):
                sleep(1.5)
                driver.execute("document.querySelector('button.btn.btn-info.nc-ok').click()")
                sleep(1.5)
                driver.execute_script("document.querySelector('a#btnAcionaCertificado.btn-block').click()")
                sleep(1.5)
                pt.press('enter')
                sleep(1.5)
        except:
            pass
        infoByPlan=requestXLSX(list())
        returnTrue=0
        #for a in testPandas.request.getFile(''):
        for a in infoByPlan.returnXLSX(''):
            sleep(0.5)
            driver.execute_script("document.querySelector('input#TxtCPF.form-control').value=''")
            inputEnter=driver.find_element(By.ID, 'TxtCPF')
            inputEnter.send_keys(f'{a}')
            sleep(1)
            driver.execute_script("document.querySelector('a#imbLocalizar').click()")
            sleep(5)
            
            returnTrue=0
            try:
                WebDriverWait(driver, 1.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
                returnTrue=returnTrue+1
                sleep(1)
                driver.execute_script("document.querySelector('button.btn.btn-info.nc-ok').click()")
                print('valor not found')
                
                pass
                
            except TimeoutException:
                driver.execute_script("console.log(document.querySelector('span#lblNomeEmpresa').innerHTML)")
                
                log=driver.get_log('browser')
                dictLog=log[-1]
                initText=dictLog['message'].find('"')
                dictLog=dictLog['message'][initText+1:len(dictLog['message'])-1]
                lista.append(dictLog)
                lista.append(a)
                sleep(5)
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
        sleep(1.5)
        pt.press('enter')
        sleep(1)
        inputEnter=driver.find_element(By.ID, 'TxtCPF')
        inputEnter.send_keys(f'{e.control.data['cnpj']}')
        print(e.control.data)
        sleep(0.5)
        driver.execute_script("document.querySelector('a#imbLocalizar').click()")
        sleep(1.5)
        if driver.title!='Empresas':
            # return content driver.switch_to.default_content()
            for a in range(0,2):
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
                sleep(5)
                iframe=driver.find_element(By.ID, 'iframe')
                driver.switch_to.frame(iframe)
                popupAtivo=False
                try:
                    #requisições mescladas efetuar alteração dos valores incluidoss
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'bootbox.modal.fade.in')))
                    print('Request ativa')
                    sleep(1)
                    pt.press(['tab', 'enter'])
                    popupAtivo=True
                    sleep(5)
                except:
                    if popupAtivo==False:
                        driver.find_element(By.ID, 'ibFechamento').click()
                        sleep(1)
                        print('Request não ativa')
                    pass
                try:
                    Select(driver.find_element(By.CLASS_NAME, 'form-control')).select_by_visible_text('Serviços Contratados')
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'bootbox.modal.fade.in')))
                        sleep(1)
                        pt.press(['tab', 'enter'])
                    except:
                        popupAtivo=False
                except:
                    if popupAtivo==False:
                        driver.find_element(By.ID, 'ibFechamento').click()
                        sleep(1)
                        print('Request não ativa')
                    pass
                driver.switch_to.default_content()
            sleep(10)
            driver.quit()
        return 
    
    def requestEmissaoLivro(e):
        driver = webdriver.Chrome()
        driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx?ReturnUrl=%2fcuiaba')
        sleep(1)
        driver.execute_script("document.querySelector('a#btnAcionaCertificado').click()")
        sleep(1.5)
        pt.press('enter')
        sleep(5)
        driver.execute_script("document.querySelector('input#TxtCPF.form-control').value=''")
        inputEnter=driver.find_element(By.ID, 'TxtCPF')
        sleep(1)
        inputEnter.send_keys(e.control.data['cnpj'])
        sleep(1)
        driver.execute_script("document.querySelector('a#imbLocalizar').click()")
        
        try:
            #criar def de loop em retorno de tentativa
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-dialog')))
            sleep(1)
            driver.execute_script("document.querySelector('button.btn.btn-info.nc-ok').click()")
        
        except TimeoutException:
            requestLivro(driver, e.control.data['name'])
        sleep(15)
        print('Finalização de requisição')
        driver.quit()
        return

    def requestAutomatic(e):
        try:
            page.add(page.open(e.control.data['spanControl']))
        except:
            pass
        sleep(1)
        execAutomatic(e.control.data['pathFile'])
        sleep(5)
        page.close(e.control.data['spanControl'])
        return
    
    

    #First row
    colunaInfo=ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        scroll='auto',expand=True  # (opcional) Alinha a coluna no centro vertical da tela
    )
    colunaInfo.controls.append(
        ft.Row(controls=[
            ft.Container(ft.Text('RAZÃO SOCIAL', weight=ft.FontWeight.BOLD), alignment=ft.alignment.center, width=400,bgcolor='#BBBBBB',border_radius=5),
            ft.Container(ft.Text('CNPJ',weight=ft.FontWeight.BOLD), alignment=ft.alignment.center, width=400,bgcolor='#BBBBBB',border_radius=5),
            ft.Container(ft.Text('EMISSÃO',weight=ft.FontWeight.BOLD), alignment=ft.alignment.center, width=400,bgcolor='#BBBBBB',border_radius=5)
        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
    )
    
    page.add(ft.Text(spans=[ft.TextSpan('Fechamento Empresas', ft.TextStyle(size=100, color=ft.Colors.BLACK, italic=False, bgcolor=ft.Colors.GREEN_100, weight=ft.FontWeight.NORMAL,  foreground=ft.Paint(gradient=ft.PaintLinearGradient((20, 100), (250, 20), [ft.Colors.BLUE, ft.Colors.PINK]) )))] ))
    listWithFunction=[ft.Column(controls=[ft.Text('Select a Controle Contábil Geral excel file'),ft.ElevatedButton('Choose files...', on_click=lambda _: file_picker.pick_files(allow_multiple=False))],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER), ft.Text('ERROR INVALID FORMAT', color=ft.Colors.RED), ft.ProgressRing(),ft.AlertDialog(modal=True, title=ft.Text('Executando automação'), actions=[ft.TextButton('Cancelar', on_click=lambda e: page.close(listWithFunction[3]))]) ]
    page.add(listWithFunction[0])
    
    def requestPageEmpresasCB():
        global lista, pathFile
        print(pathFile)
        while len(lista)>0:
            #Alimentando as colunas com respectivas linhas com valores referenciados
            widget=[ft.ElevatedButton(text='GUIAS', data={'cnpj':lista[0], 'name':lista[1]},on_click=requestEmitir), ft.ElevatedButton(text='NFS', data={'cnpj':lista[0], 'name':lista[1]}, on_click=ExecuteEmissoes),ft.ElevatedButton(text='LIVRO', data={'cnpj':lista[0], 'name':lista[1]}, on_click=requestEmissaoLivro),ft.ElevatedButton(text='NOTAS TOMADAS', data={'cnpj':lista[0], 'name':lista[1]}, on_click=emitirNotasTomadas)]
            
            colunaInfo.controls.append(
                ft.Row(
                controls=[
                    
                    ft.Container(ft.Text(lista[1]), alignment=ft.alignment.center, width=400,bgcolor='#D9DAD9',border_radius=5),
                    ft.Container(ft.Text(lista[0]), alignment=ft.alignment.center, width=400,bgcolor='#D9DAD9',border_radius=5),
                    ft.Container(content=ft.Row(controls=widget, alignment=ft.MainAxisAlignment.SPACE_AROUND) , alignment=ft.alignment.center, width=400,border_radius=5)
                    
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            )
            del lista[0]
            sleep(0.5)
            del lista[0]
            print(len(lista))
        sleep(5)
        page.remove(listWithFunction[2])
        page.add(
            ft.ElevatedButton(text='Executar Automação', data={'pathFile':pathFile,'spanControl':listWithFunction[3]},on_click=requestAutomatic),
            colunaInfo,

        )
        page.update()

    return

def requestMSG(msg):
    return print(msg.control.key)

ft.app(target=mainFletApp, assets_dir='/')