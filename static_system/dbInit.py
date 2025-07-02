import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pyautogui as pt
from time import sleep
from datetime import datetime
from datetime import date as dt
import requests
import os
import shutil
import json

class requestFileXLSX:
    def __init__(self,  page, filePath: str):
        if filePath=='':
            fileXLSX=pd.read_excel('Responsabilidade Tecnica.xlsx', sheet_name=0)
            self.dataRefinement={}
            enumerateID=0
            for i in range(len(fileXLSX['REGIME'])):
                if fileXLSX['CNPJ'][i]!='NÃO' and isinstance(fileXLSX['Nº8'][i], int):
                    
                    self.dataRefinement[f'{fileXLSX['Nº8'][i]}']=[fileXLSX['NOME DA EMPRESA'][i], fileXLSX['CNPJ'][i], fileXLSX['CIDADE'][i], fileXLSX['REGIME'][i]]
        else:
            try:
                self.dataRefinement={}
                self.dataRefinement['code']=[i for i in pd.read_excel(filePath)['CODIGO']]
                self.dataRefinement['razao']=[i for i in pd.read_excel(filePath)['RAZAO']]
                self.dataRefinement['cnpj']=[i for i in pd.read_excel(filePath)['DOCUMENTO']]
                self.dataRefinement['tributacao']=[i[4:] for i in pd.read_excel(filePath)['TRIBUTACAO']]
                self.dataRefinement['cep']=[i for i in pd.read_excel(filePath)['CEP']]
                self.dataRefinement['ie']=[i if i != '' else 'Null' for i in pd.read_excel(filePath)['IE'] ]
                self.dataRefinement['im']=[i if i != '' else 'Null' for i in pd.read_excel(filePath)['IM'] ]    
            except Exception as e:    
                print(f'ERROR {e}')
            finally:
                print('success')

        return None
    
    def requestData(self):
        return self.dataRefinement

#dataRefinement=requestFileXLSX('', 'Company.xlsx').requestData()
dataRefinement=requestFileXLSX('', '').requestData()


def requestISSQN(parametro):
    driver=webdriver.Chrome()
    driver.get('https://onlinecba.issnetonline.com.br/cuiaba/Login/Login.aspx')
    driver.maximize_window()
    AcionarCertificado=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'btnAcionaCertificado')))
    AcionarCertificado.click()
    sleep(1.5)
    pt.press('enter')
    sleep(5)
    driver.find_element(By.ID, 'TxtCPF').send_keys(parametro)
    driver.find_element(By.ID, 'imbLocalizar').click()
    sleep(5)
    if str(driver.title) == 'ISSNet On-Line - Nota Eletrônica':
        driver.quit()
        return True
    else:
        driver.quit()
        return False


class RequestFolder:
    'entrada, saida, emissor, tomador, prestados'
    def __init__(self, filePath, code):
        ntFolder=['entrada', 'saida', 'emissor', 'tomador', 'prestados']
        self.pathsToResearch=[]
        self.filePath=filePath
        for i in ntFolder:
            pathRoute=r'\\192.168.110.251\geral\Gestor Sistema\XML'
            pathRoute=os.path.join(pathRoute, self.filePath)
            pathRoute=os.path.join(pathRoute, i)
            try:
                pathRoute=os.path.join(pathRoute, f'{code}-I')
                for files in os.listdir(os.path.join(pathRoute, f'0{int(datetime.today().month)-1}2025')):
                    self.pathsToResearch.append(os.path.abspath(os.path.join(pathRoute, f'0{int(datetime.today().month)-1}2025')))
                    break
            except Exception as e:
                print(f'Not files {e}')
                continue
        return None
    def moveFolder(self, pathDestiny):
        folderDestiny=os.path.join(os.path.abspath(f'arquivosApi/{pathDestiny}/'), self.filePath)
        for i in self.pathsToResearch:
            try:
                #debbug this line
                os.makedirs(folderDestiny, exist_ok=True)
                contador=1
                for files in os.listdir(i):
                    nome, ext=os.path.splitext(files)
                    remetente=os.path.join(i, files)
                    shutil.copy2(remetente, os.path.join(folderDestiny, f'{str(self.filePath).upper()}{int(dt.today().month)-1}-{dt.today().year}_{contador}{ext}')) if f'{str(self.filePath).upper()}{int(dt.today().month)-1}-{dt.today().year}_{contador}{ext}' not in os.listdir(folderDestiny) else False
                    contador+=1

            except Exception as e:
                print(f'Error to create folder {folderDestiny} {e}')
        
        return

DATABASE='evasystem/bin/data/files.db'
DATABASEUSERS='evasystem/bin/data/users.db'

class Users:
    def __init__(self, runDB) -> sqlite3.Connection:
        self.runDB=sqlite3.connect(DATABASEUSERS, timeout=10.0)
        self.runDB.cursor().execute("""
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            
            acesso_A BOOLEAN DEFAULT 0,
            acesso_B BOOLEAN DEFAULT 0,
            acesso_C BOOLEAN DEFAULT 0,

            email TEXT UNIQUE,
            hash TEXT UNIQUE NOT NULL
                            
            )""")
        self.runDB.row_factory=sqlite3.Row
        
        #ativação WAL
        mode=self.runDB.execute("PRAGMA journal_mode=WAL;")
        mode=mode.fetchone()[0]
        if mode.upper()!='WAL':
            raise RuntimeError(f'Wal não habilitado, retornou: {mode}')
        else:
            print('WAL Habilitado')
        return None
        
    #log de requisição
    def logRequest(self, sql: str, params:tuple=()):
        with open('temp/usersLog.txt', 'a') as log:
            log.write(f'[{datetime.now().isoformat()}] SQL: {sql} | PARAMS: {params}\n')
        return
    
    #commit db inserção e acesso
    def commit_and_requestDB(self, sqlContext:str, param:tuple=(), get_access=0):
        if get_access==0:
            try:
                dictConvert=[dict(data) for data in self.runDB.cursor().execute(sqlContext)]
                return dictConvert 
            except Exception as e:
                print(f'Erro {e}')
            finally:
                self.runDB.close()
        else:
            try:
                self.runDB.cursor().execute(sqlContext, param)
                self.runDB.commit()
            except Exception as e:
                self.runDB.rollback()
                print(f'Error {e}')
            finally:
                self.runDB.close()

    
    def request_delete_db(self):
        self.runDB.cursor().execute('DELETE FROM users')
        self.runDB.commit()
        return 'DB deleted'
    

class RequestDB:
    def __init__(self, runDB) -> sqlite3.Connection:
        self.runDB=sqlite3.connect(DATABASE, timeout=10.0)
        self.runDB.cursor().execute('''
            CREATE TABLE IF NOT EXISTS  company(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo INTEGER UNIQUE NOT NULL,
            razao TEXT NOT NULL,
            cnpj TEXT NOT NULL UNIQUE,
            cidade TEXT DEFAULT Null,
            modalidade TEXT NOT NULL,
            ie TEXT DEFAULT Null,
            im TEXT DEFAULT Null,
            issqn TEXT DEFAULT Null
            )
        
        ''')
        
        self.runDB.row_factory=sqlite3.Row
        #habilitando o WAL
        #self.runDB.execute("PRAGMA synchronous=NORMAL;") melhora o desempenho de requisição do banco
        mode=self.runDB.execute("PRAGMA journal_mode=WAL;")
        mode=mode.fetchone()[0]
        if mode.upper()!='WAL':
            raise RuntimeError(f'Não foi habilitado o Wal, journal_mode retornou: {mode}')
        else:
            print('WAL Habilitado!')
        return None

    #grava os log de requisição por parte dos users
    def logRequest(self, sql: str, params: tuple=()):
        with open('temp/access_logDB.txt', 'a', encoding='utf-8') as log:
            log.write(f'[{datetime.now().isoformat()}] SQL: {sql} | PARAMS: {params}\n')
        return 

    def iniciarDB(self):
        self.runDB=sqlite3.connect(DATABASE, timeout=10.0)
        return self.runDB('')

    def requestCommitOtimized(self, sqlContext: str, param: tuple=()):
        try:
            self.runDB.cursor().execute(sqlContext, param)
            self.runDB.commit()
        except Exception as e:
            self.runDB.rollback()
            print(f'Erro: {e}')
        finally:
            self.runDB.close()
    
    def getData(self, sqlContext: str, clientSide):
        try:
            dictConvert=[dict(data) for data in self.runDB.execute(sqlContext).fetchall()]
            self.logRequest(sqlContext, (f'client: {clientSide}'))
            return dictConvert
        except Exception as e:
            self.runDB.rollback()
            raise e
        finally:
            self.runDB.close()

    #encerra a conexão com o banco
    def closeConn(self):
        return self.runDB.close()

    #retorna todos os valores referente ao banco
    def GetFile(self, parametro, clientSide):
        try:
            if str(parametro).strip().upper()=='LUCRO PRESUMIDO' or str(parametro).strip().upper()=='LUCROPRESUMIDO':
                SQLcontext='SELECT * FROM EnterpriseLucroPresumido'
                dictConvert=[dict(data) for data in self.runDB.execute(SQLcontext).fetchall()]
                self.logRequest(SQLcontext, ('Request All DataBase', clientSide))
                return dictConvert
            elif str(parametro).strip().upper()=='SIMPLES NACIONAL' or str(parametro).strip().upper()=='SIMPLESNACIONAL' or str(parametro).strip().upper()=='SIMPLES ME':
                SQLcontext='SELECT * FROM EnterpriseSimplesNacional'
                dictConvert=[dict(data) for data in self.runDB.execute(SQLcontext).fetchall()]
                self.logRequest(SQLcontext, ('Select All DataBase', clientSide))
                return dictConvert
            else:
                return 'Error modalidade não inclusa'
        
        except Exception as e:
            return f'error to return data {e}'
    
    #retorna o valor de uma coluna em especifico
    def GetSpecificColumn(self, coluna, modalidade):
        try:
            if str(modalidade).strip().upper()=='LUCRO PRESUMIDO' or str(modalidade).strip().upper()=='LUCROPRESUMIDO':
                SQLcontext=f"SELECT {coluna} FROM EnterpriseLucroPresumido"
                dictConvert=[dict(data) for data in self.runDB.execute(SQLcontext).fetchall()]
                self.logRequest(SQLcontext, 'Request column')
                return dictConvert
            elif str(modalidade).strip().upper()=='SIMPLES NACIONAL' or str(modalidade).strip().upper()=='SIMPLESNACIONAL' or str(modalidade).strip().upper()=='SIMPLES ME':
                SQLcontext=f"SELECT {coluna} FROM EnterpriseSimplesNacional"
                dictConvert=[dict(data) for data in self.runDB.execute(SQLcontext).fetchall()]
                self.logRequest(SQLcontext, 'Request column')
                return dictConvert
        except Exception as e:
            return f'Erro to request column/data {e}'
    
    def GetRowValue(self, modalidade, id, clientSide):
        try:
            if str(modalidade).strip().upper()=='LUCRO PRESUMIDO' or str(modalidade).strip().upper()=='LUCROPRESUMIDO':
                SQLcontext=f"SELECT * FROM EnterpriseLucroPresumido WHERE id={id}"
                dictConvert=[dict(data) for data in self.runDB.execute(SQLcontext).fetchall()]
                self.logRequest(SQLcontext, ('Request a Row', clientSide))
                return dictConvert
            elif str(modalidade).strip().upper()=='SIMPLES NACIONAL' or str(modalidade).strip().upper()=='SIMPLESNACIONAL' or str(modalidade).strip().upper()=='SIMPLES ME':
                SQLcontext=f"SELECT * FROM EnterpriseSimplesNacional WHERE id={id}"
                dictConvert=[dict(data) for data in self.runDB.execute(SQLcontext).fetchall()]
                self.logRequest(SQLcontext, ('Request a Row', clientSide))
                return dictConvert
        except Exception as e:
            return f'Erro to request column/data {e}'

    #efetua a adição de um valor ao banco
    def PostFile(self, registerFlag, CODE, RAZAO, CNPJ, CIDADE, MODALIDADE):
        try:
            if str(registerFlag).strip().upper()=='LUCRO PRESUMIDO' or str(registerFlag).strip().upper()=='LUCROPRESUMIDO':
                dataUnique=[dict(i) for i in self.runDB.execute('SELECT cnpj FROM EnterpriseLucroPresumido').fetchall()]
                dataUnique=[i['cnpj'] for i in dataUnique]
                if CNPJ not in dataUnique:
                    self.runDB.execute("INSERT INTO EnterpriseLucroPresumido (codigo, razao, cnpj, cidade, modalidade) VALUES (?, ?, ?, ?, ?)", (f'{CODE}',f'{RAZAO}', f'{CNPJ}', f'{CIDADE}', f'{MODALIDADE}'))
                    sleep(1)
                    self.runDB.commit()
                    return 'data saved'
                else:
                    return 'Data já no banco'
            elif str(registerFlag).strip().upper()=='SIMPLES NACIONAL' or str(registerFlag).strip().upper()=='SIMPLESNACIONAL':
                dataUnique=[dict(i) for i in self.runDB.execute('SELECT cnpj FROM EnterpriseSimplesNacional').fetchall()]
                dataUnique=[i['cnpj'] for i in dataUnique]
                if CNPJ not in dataUnique:
                    self.runDB.execute("INSERT INTO EnterpriseSimplesNacional (codigo, razao, cnpj, cidade, modalidade) VALUES (?, ?, ?, ?, ?)", (f'{CODE}', f'{RAZAO}', f'{CNPJ}', f'{CIDADE}', f'{MODALIDADE}'))
                    self.runDB.commit()
                    return 'data saved'
                else:
                    return 'Data já no banco'
            else:
                return 'Error Modalidade invalida'
        except Exception as e:
            return f'Erro to save data {e}'
    
    def DelFile(self, parametro, modal):
        if modal=='SIMPLES ME':
            self.runDB.execute(f"DELETE FROM EnterpriseSimplesNacional WHERE id = {parametro}")
            self.runDB.commit()
            self.runDB.close()
        elif modal=='LUCRO PRESUMIDO':
            self.runDB.execute(f"DELETE FROM EnterpriseLucroPresumido WHERE id = {parametro}")
            self.runDB.commit()
            self.runDB.close()
        else:
            return 'error'

    def requestDeleteDB(self, dbName):
        self.runDB.execute(f"DELETE FROM Enterprise{dbName}")
        self.runDB.commit()
        pass
    
    #atualiza os valores de um banco de dados
    def requestAttDB(self, endpoint):
        try:
            if dataRefinement['cep']: 
                for i in range(len(dataRefinement['cep'])):
                    sleep(1)
                    try:
                        state=requests.get(f"https://brasilapi.com.br/api/cep/v1/{dataRefinement['cep'][i]}").json()
                        cidade=f'{state['city']}-{state['state']}'
                    except:
                        print(f'Error cep:{dataRefinement['cep'][i]}')
                        cidade='None'
                    finally:
                        print(f'Success Request {cidade}')
                    try:
                        if dataRefinement['tributacao'][i]==str(endpoint).upper():

                            self.runDB.cursor().execute("INSERT INTO EnterpriseLucroPresumido (codigo, razao, cnpj, cidade, modalidade, ie, im) VALUES (?,?,?,?,?,?,?)", (dataRefinement['code'][i], dataRefinement['razao'][i], dataRefinement['cnpj'][i], cidade, dataRefinement['tributacao'][i], dataRefinement['ie'][i], dataRefinement['im'][i]))
                            self.runDB.commit()
                        elif dataRefinement['tributacao'][i]=='SIMPLES ME' and endpoint=='simples nacional':
                            self.runDB.cursor().execute("INSERT INTO EnterpriseSimplesNacional (codigo, razao, cnpj, cidade, modalidade, ie, im) VALUES (?,?,?,?,?,?,?)", (dataRefinement['code'][i], dataRefinement['razao'][i], dataRefinement['cnpj'][i], cidade, dataRefinement['tributacao'][i], dataRefinement['ie'][i], dataRefinement['im'][i]))
                            self.runDB.commit()
                    except Exception as e:
                        print(f'Erro company: {dataRefinement['cnpj'][i]} cep:{dataRefinement['cep'][i]} tributação:{dataRefinement['tributacao'][i]}')
                        print(f'CODE: {e}')
                        continue  
                    #print(requests.get(f'https://brasilapi.com.br/api/cep/v2/{dataRefinement['cep'][i]}').json()['city']+'-'+requests.get(f'https://brasilapi.com.br/api/cep/v2/{dataRefinement['cep'][i]}').json()['state'])
        except:
            try:
                for i in dataRefinement:
                    print(dataRefinement[i])
                    dictDB=[dict(i) for i in self.runDB.execute('SELECT * FROM company').fetchall()]
                    cnpj_verify=[i['cnpj'] for i in dictDB ]
                    print(cnpj_verify)
                    try:
                        if dataRefinement[i][2] not in cnpj_verify:
                            self.runDB.execute('INSERT INTO company (codigo, razao, cnpj, cidade, modalidade) VALUES (?,?,?,?,?)', (i, dataRefinement[i][0],dataRefinement[i][1],dataRefinement[i][2],dataRefinement[i][3]))
                            self.runDB.commit()
                    except:
                        continue
            except Exception as e:
                print(f'Error {e}')
        self.runDB.close()

    def requestGestorFiles(self, db):
        listFilesGet=['cte','nfce','nfe','nfse']
        code=[dict(i) for i in self.runDB.execute(f"SELECT codigo FROM Enterprise{db}").fetchall()]
        cnpj=[dict(i) for i in self.runDB.execute(f"SELECT cnpj FROM Enterprise{db}").fetchall()]
        refinedList={'codes':[],'cnpjs':[]}
        for i in code:
            if i['codigo']!='None':
                refinedList['codes'].append(i['codigo'])
        for i in cnpj:
            refinedList['cnpjs'].append(i['cnpj'])
        
        #gera a requisição dos arquivos citados na listFileGet
        for archive in listFilesGet:
            for i in range(len(refinedList['codes'])):
                try:
                    RequestFolder(archive, refinedList['codes'][i]).moveFolder(f'{refinedList['cnpjs'][i][:10]+refinedList['cnpjs'][i][11:]}')
                    print('Moved success')
                except:
                    print(f'Error to request {refinedList['cnpjs'][i]}')
                    continue
            
    
#RequestDB('').requestAttDB('')
#RequestDB('').requestDeleteDB('SimplesNacional')
#print(RequestDB('').requestAttDB('simples nacional'))
#print(RequestDB('').requestAttDB('lucro presumido'))
#print(RequestDB('').requestGestorFiles('LucroPresumido'))