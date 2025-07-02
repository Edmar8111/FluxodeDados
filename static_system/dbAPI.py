import os
import re
import sys
import json
import shutil
import sqlite3
import pandas as pd
import dbInit as db
import requests
from time import sleep
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from bs4 import BeautifulSoup
from datetime import datetime as dt
from flask import Flask, g, jsonify, render_template, send_file, request, send_from_directory, url_for, redirect


UPLOAD_FOLDER='arquivosApi'
ACCESS_FOLDER='evasystem'




app=Flask(__name__)

#retorna a pagina de erro
@app.errorhandler(404)
def pageNotFound(e):
    print(e)
    if e!='':
        return render_template('errorPage.html', msg=e), 404
    else:
        return render_template('errorPage.html')
    
#pagina inicial
@app.route('/')
def firstPage():
    file_css='pagina_index.css'
    file_js='pagina_index.js'
    return render_template('pagina_index.html', info_file=[file_css, file_js], refresh=[0])

def rt_login():
    return jsonify('Success')

@app.route('/gerarfile/<modalidade>/<id>')
def gerar_DeSTDA(modalidade, id):
    if str(modalidade).upper()=='SIMPLES ME':
        company_info=db.RequestDB('').GetRowValue(modalidade, id, request.remote_addr)
    elif str(modalidade).upper()=='LUCRO PRESUMIDO':
        company_info=db.RequestDB('').GetRowValue(modalidade, id, request.remote_addr)
    else:
        return jsonify('error')
    
    if company_info[0]['ie']!='Null' and company_info[0]['im']!='Null':
        company_cnpj=re.sub(r'\D','', company_info[0]['cnpj'])
        company_ie=company_info[0]['ie']
        company_im=company_info[0]['im']
        #True if company_im[-2]=='.0' else False
        data_inicio='01052025'
        data_fim='31052025'
        info_json=requests.get(f'https://publica.cnpj.ws/cnpj/{company_cnpj}').json()
        sleep(1)
        infoValue={
            'CNPJ':company_cnpj,
            'RAZAO':info_json['razao_social'],
            'SOCIO':info_json['socios'][0]['nome'],
            'CPF_SOCIO':info_json['socios'][0]['cpf_cnpj_socio'],
            'EMAIL':info_json['estabelecimento']['email'],
            'LOGRADOURO':info_json['estabelecimento']['logradouro'],
            'BAIRRO':info_json['estabelecimento']['bairro'],
            'ATIVIDADE':info_json['estabelecimento']['atividade_principal']['id'],
            'CEP':info_json['estabelecimento']['cep'],  
            'TEL1':info_json['estabelecimento']['telefone1'],
            'NUMERO':info_json['estabelecimento']['numero'],
            'CIDADE_CODE':info_json['estabelecimento']['cidade']['ibge_id'],
            'UF':info_json['estabelecimento']['estado']['sigla'],
            'INSCRICAO':info_json['estabelecimento']['inscricoes_estaduais'][0]['inscricao_estadual']}
        
        conteudo = f"""|0000|LFPD|{data_inicio}|{data_fim}|{infoValue['RAZAO']}|{infoValue['CNPJ']}|{infoValue['UF']}|{company_ie}|{infoValue['CIDADE_CODE']}|{company_im}|||2000|0|30|Brasil|||||
|0001|1|
|0005|{infoValue['SOCIO']}|999|{infoValue['CPF_SOCIO']}|{infoValue['CEP']}|{infoValue['LOGRADOURO']}|{infoValue['NUMERO']}||{infoValue['BAIRRO']}|||{infoValue['TEL1']}||{infoValue['EMAIL']}|
|0030|1|7|0|0||||||||||||||
|0100|TALLY UP CONTABILIDADE DIGITAL LTDA|900|25064145000187|99489368172|MT001835O4||ANTIGUA|99||JARDIM DAS AMERICAS|MT|5103403|||||CONTABILIDADE@TALLYUP.COM.BR|
|0990|6|
|G001|1|
|G020|9|{data_inicio}|{data_fim}|
|G600|||0,00|
|G605|0|||0,00|
|G605|1|||0,00|
|G605|2|||0,00|
|G605|3|||0,00|
|G620|1|0|||0,00|0,00|
|G625|{infoValue['UF']}|0|||0,00|
|G625|{infoValue['UF']}|1|||0,00|
|G625|{infoValue['UF']}|2|||0,00|
|G625|{infoValue['UF']}|3|||0,00|
|G990|13|
|9001|1|
|9900|0000|1|
|9900|0001|1|
|9900|0005|1|
|9900|0030|1|
|9900|0100|1|
|9900|0990|1|
|9900|G001|1|
|9900|G020|1|
|9900|G600|1|
|9900|G605|4|
|9900|G620|1|
|9900|G625|4|
|9900|G990|1|
|9900|9001|1|
|9900|9990|1|
|9900|9999|1|
|9900|9900|17|
|9990|20|
|9999|39|
"""
    
    file_name='DeSTDA_MT_042025.txt'
    with open(f'{file_name}','w', encoding='utf-8') as file:
        file.write(conteudo)
    try:
        if not os.path.isfile(os.path.join(ACCESS_FOLDER, f'{company_cnpj}/{file_name}')): 
            os.makedirs(os.path.join(ACCESS_FOLDER, f'{company_cnpj}/DeSTDA/'), exist_ok=True)
            shutil.move(f'{file_name}', os.path.join(ACCESS_FOLDER,f'{company_cnpj}/DeSTDA/'))
            path_file=os.path.join(ACCESS_FOLDER,f'{company_cnpj}/DeSTDA/')
            return send_file(os.path.join(path_file, f'{file_name}'), as_attachment=True)
        else:
            return pageNotFound('DeSTDA do mes já baixado!')
    except:
        return pageNotFound('DeSTDA Não Baixado')

#pagina que efetua login
@app.route('/login/page', methods=['POST','GET'])
def loginPage():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('senha')

        for i in db.Users('').commit_and_requestDB("SELECT * FROM users", 0):
            print(os.path.isdir(os.path.join(os.path.join(ACCESS_FOLDER, 'conf/firewall/usersFolder/'), i['username'])))
            print(i['email'])
            try:
                    if os.path.isfile(os.path.join(os.path.join(ACCESS_FOLDER, f'conf/firewall/usersFolder/{i["username"]}'), 'password.aes')) and email==i['email']:
                        
                        with open(os.path.join(os.path.join(ACCESS_FOLDER, f'conf/firewall/usersFolder/{i["username"]}'), 'vetor.bin'), 'rb') as f:
                            vetor=f.read()
                        with open(os.path.join(os.path.join(ACCESS_FOLDER,f'conf/firewall/usersFolder/{i["username"]}'), 'keyUser.bin'), 'rb') as f:
                            key=f.read()
                        key_decrypt=AES.new(key, AES.MODE_CBC, vetor)
                        
                        try:
                            with open(os.path.join(os.path.join(ACCESS_FOLDER,f'conf/firewall/usersFolder/{i["username"]}'), 'password.aes'), 'rb') as data:
                                variavel=unpad(key_decrypt.decrypt(data.read()), AES.block_size)
                            
                            if password==variavel.decode():
                                os.makedirs(os.path.join(os.path.join(ACCESS_FOLDER,'conf/firewall/usersFolder/'), i['username']), exist_ok=True)
                                
                                #caso o arquivo json do usuario não tenha sido criado
                                if not os.path.isfile(os.path.join(os.path.join(ACCESS_FOLDER,f'conf/firewall/usersFolder/{i['username']}'),'data.json')):
                                    print('request')
                                    with open(os.path.join(ACCESS_FOLDER,'conf/firewall/hash.json'), 'r', encoding='utf-8') as file:
                                        data=json.load(file)
                                    data['login']='True'
                                    data['HASH']=i['hash']
                                    with open('data.json', 'w', encoding='utf-8') as dados:
                                        json.dump(data, dados, indent=4, ensure_ascii=False)
                                    shutil.move('data.json', os.path.join(os.path.join(ACCESS_FOLDER,'conf/firewall/usersFolder/'), i['username']))

                                return jsonify('logado')
                            else:
                                return jsonify('Senha incorreta')
                        except Exception as e:
                            return jsonify(f'Error on user {i["username"]}')
                        
            except:
                continue

    else:
        return render_template('loginIndex.html')

@app.route('/cnae/<param>',methods=['GET', 'POST'])
def return_cnae(param):
    if request.method=='POST':
        cnae_info=0
        with open('cnaes.json', 'r', encoding='utf-8') as data, open('anexo_info.json', 'r', encoding='utf-8') as file:
            data_file=json.load(data)
            file_data=json.load(file)
        try:
            for i in range(len(data_file['CNAES'])):
                if param==data_file['CNAES'][i]['id']: 
                    cnae_info=data_file['CNAES'][i]
                    break
            for i in range(len(file_data)):
                if param==file_data[i]['codigo']: 
                    cnae_info['anexo_info']=file_data[i]
                    break
        except Exception as e:
            print(f'Error to return CNAE info {e}')    
        finally:
            if cnae_info!=0:
                print(cnae_info['anexo_info'])      
                return jsonify(cnae_info)

    return render_template('pagina_cnae.html',items=['pagina_cnae.css','pagina_cnae.js'], refresh=[0])

#pagina de criação de conta
@app.route('/registerAccount/page', methods=['POST','GET'])
def registerPage():
    verify_user_inf=db.Users('').commit_and_requestDB('SELECT * FROM users', 0)
    users_active=[i['username'] for i in verify_user_inf]
    email_active=[i['email'] for i in verify_user_inf]
    hashes_active=[i['hash'] for i in verify_user_inf]
    
    if request.method=='POST':
        username=request.form.get('nome')
        email=request.form.get('email')
        sys.path.append(r'C:\Users\edmar\desktop\debug folder\evasystem\conf\firewall')
        import generate
        hash_gen=generate.v
        
        
        if request.form.get('nome') not in users_active and request.form.get('email') not in email_active:
            #efetuar refatoração
            try:
                #encriptação
                os.makedirs(os.path.join(os.path.join(ACCESS_FOLDER,'conf/firewall/usersFolder/'), username), exist_ok=True)
                with open('keyUser.bin', 'wb') as file:
                    os.makedirs(f'/{file.write(hash_gen.encode('utf-8')[:32])}', exist_ok=True)
                    
                vetor=get_random_bytes(16)
                with open('vetor.bin', 'wb') as data:
                    os.makedirs(f'/{data.write(vetor)}', exist_ok=True)
                

                object_encrypt=AES.new(hash_gen.encode('utf-8')[:32], AES.MODE_CBC, vetor)
                filling_bytes=pad(request.form.get('senha').encode('utf-8'), AES.block_size)
                encrypt_pass=object_encrypt.encrypt(filling_bytes)
                with open('password.aes', 'wb') as f:
                    os.makedirs(os.path.join(ACCESS_FOLDER, f'conf/firewall/usersFolder/{username}'), f.write(encrypt_pass), exist_ok=True)
                
                shutil.move(os.path.abspath('password.aes'),os.path.join(ACCESS_FOLDER,f'conf/firewall/usersFolder/{username}'))
                db.Users('').commit_and_requestDB('INSERT INTO users (username, acesso_A, acesso_B, acesso_C, email, hash) VALUES (?,?,?,?,?,?)', (f'{username}', 0,0,0, f'{email}', f'{hash_gen}'), 1)
                shutil.move(os.path.abspath('keyUser.bin'), os.path.join(ACCESS_FOLDER, f'conf/firewall/usersFolder/{username}/') )
                shutil.move(os.path.abspath('vetor.bin'), os.path.join(ACCESS_FOLDER,f'conf/firewall/usersFolder/{username}/'))
                print('Todos as bin geradas')
                return jsonify('Valor inserido ao banco')
            
            except Exception as e:
                os.remove(os.path.abspath('keyUser.bin')) if os.path.isfile(os.path.abspath('keyUser.bin')) else False                
                os.remove(os.path.abspath('vetor.bin')) if os.path.isfile(os.path.abspath('vetor.bin')) else False
                try:
                    shutil.rmtree(os.path.join(ACCESS_FOLDER,f'conf/firewall/usersFolder/{username}/'))
                except:
                    try:
                        os.rmdir(os.path.join(ACCESS_FOLDER,f'conf/firewall/usersFolder/{username}/'))
                    except Exception as e:
                        print(f'Diretorio não encontrado: {e}')
                
                return jsonify(f'Erro ao cadastrar usuario: {e}')
           
        else:
            return pageNotFound('')
    else:
        return render_template('createLogin.html')

#efetua requisição do lucro presumido
@app.route('/page/lucroPresumido')
def requestGetLP(message=''):
    try:
        queryDB=("SELECT * FROM company")
        itens0=db.RequestDB('').getData(queryDB, request.remote_addr)
        itens=[]
        for i in itens0:
            if i['modalidade']=='LUCRO PRESUMIDO':
                itens.append({'id':i['id'], 'codigo':i['codigo'], 'razao':i['razao'], 'cnpj':i['cnpj'], 'cidade':i['cidade'], 'modalidade':i['modalidade'], 'ie':i['ie'], 'im':i['im'], 'issqn':i['issqn']})

    except:
        return pageNotFound('')
    finally:
        return render_template('pagina_inicial.html', items=[itens, 'lucroPresumido'], info_file=['pagina_inicial.css','pagina_inicial.js'], refresh=[1])

#efetua requição do simples
@app.route('/page/simplesNacional')
def requestGetSN():
    try:
        queryDB=("SELECT * FROM company")
        itens0=db.RequestDB('').getData(queryDB, request.remote_addr)
        itens=[]
        for i in itens0:
            if i['modalidade']=='SIMPLES NACIONAL':
                itens.append({'id':i['id'], 'codigo':i['codigo'], 'razao':i['razao'], 'cnpj':i['cnpj'], 'cidade':i['cidade'], 'modalidade':i['modalidade'], 'ie':i['ie'], 'im':i['im'], 'issqn':i['issqn']})
    except:
        return pageNotFound('')
    finally:
        return render_template('pagina_inicial.html', items=[itens, 'simplesNacional'], info_file=['pagina_inicial.css','pagina_inicial.js'], refresh=[2])

#retorna a pagina de cadastro empresas
@app.route('/page/register/<modalidade>')
def registerEnter(modalidade):
    if modalidade=='lucroPresumido':
        return render_template('register.html', item='lucroPresumido')
    elif modalidade=='simplesNacional':
        return render_template('register.html', item='simplesNacional')
    else:
        return pageNotFound('')

#aloca as imagens para efetuar retorno
@app.route('/imgtrack/<imageName>')
def imgRequest(imageName):
    #log de acesso
    with open(os.path.join(ACCESS_FOLDER,'conf/log/image_access_log.txt'), 'a') as log:
        log.write(f'Acesso: {imageName} - {request.remote_addr} - {dt.now()}\n')

    #path to image
    imagePath=f'static/images/{imageName}'
    #retorna a imagem
    return send_file(imagePath, mimetype='image/png')

#pagina da empresa
@app.route('/page/<modalidade>/<id>')
def requestFrontData(id, modalidade):
    if id!='' and modalidade!='':
        verify_files={"guias":0,"livros":0,"nfse":0,"notasT":0}
        itens=db.RequestDB('').getData(f"SELECT * FROM company WHERE id={id}", request.remote_addr)
        cnpj_folder=re.sub(r'\D','',itens[0]['cnpj'])
        
        try:
            if len(os.listdir(os.path.abspath(f'arquivosApi/{cnpj_folder}/guias')))>0:
                verify_files['guias']=1
        except:
            pass
        try:
            if len(os.listdir(os.path.abspath(f'arquivosApi/{cnpj_folder}/livros')))>0:
                verify_files['livros']=1
        except:
            pass
        try:
            if len(os.listdir(os.path.abspath(f'arquivosApi/{cnpj_folder}/nfse')))>0:
                verify_files['nfse']=1
        except:
            pass
        try:
            if len(os.listdir(os.path.abspath(f'arquivosApi/{cnpj_folder}/notasT')))>0:
                verify_files['notasT']=1
        except:
            pass


        print(verify_files)
        return render_template('onlyPage.html', items=[itens, modalidade], files=verify_files)
    else:
        return pageNotFound('')

#retorna o arquivo selecionado pelo usuario
@app.route('/arquivosApi/<directory>/<files>')
def fileRequest(directory, files):
    if os.path.isdir(f'arquivosApi/{directory}/{files}'):
        dataFile=[v for v in os.listdir(f'arquivosApi/{directory}/{files}')]
        print(dataFile)
    try:
        return render_template('filePage.html', items=[dataFile, directory, files], files=['files_page.css', 'files_page.js'])
    except:
        return pageNotFound('')

#efetua a abertura do arquivo para leitura
@app.route('/arquivosApi/<folder>/<direct>/<path:filename>')
def viewFile(folder,direct, filename):
    try:
        with open(os.path.abspath(f'{UPLOAD_FOLDER}/{folder}/{direct}/{filename}'), 'rb') as f:
            if BeautifulSoup(f.read(), 'html.parser').find(class_='Rel-TituloRelatorio').text!='Declaração de Não Movimentação – Serviços Contratados':
                print('REQUEST')   
        os.isfile(os.path.join(f'{UPLOAD_FOLDER}/{folder}/{direct}',filename)) 
    except:
        return pageNotFound('')
    finally:
        return send_from_directory(os.path.join(f'{UPLOAD_FOLDER}/{folder}/{direct}'),filename) 

#efetua a edição de uma empresa selecionada pelo usuario
@app.route('/page/edit/<modalidade>/<id>', methods=['GET','POST'])
def editCompany(modalidade, id):
    cacheData=None
    try:
        if modalidade=='LUCRO PRESUMIDO':
            cacheData=db.RequestDB('').GetRowValue('lucroPresumido', id, request.remote_addr)
        elif modalidade=='SIMPLES ME':
            cacheData=db.RequestDB('').GetRowValue('simplesNacional', id, request.remote_addr)
    except Exception as e:
            print(f'Error request data {e}')
    
    if request.method=='GET':
        print('request')
        if modalidade=='LUCRO PRESUMIDO':
            itens=db.RequestDB('').GetRowValue('lucroPresumido', id, request.remote_addr)
            return render_template('register.html', itens=itens[0], item='lucroPresumido')
        elif modalidade=='SIMPLES ME':
            itens=db.RequestDB('').GetRowValue('simplesNacional', id, request.remote_addr)
            return render_template('register.html', itens=itens[0], item='simplesNacional')
        else:
            return pageNotFound('')
    
    elif request.method=='POST' and cacheData!=None:
        print(f"ID: {id}")
        print(f"""
            json file                 fron file
            {cacheData[0]['razao']} - {request.form.get('razao')}
            {cacheData[0]['cnpj']} - {request.form.get('cnpj')}
            {cacheData[0]['cidade']} - {request.form.get('cidade')}
            {cacheData[0]['modalidade']} - {request.form.get('regime')}
            {cacheData[0]['ie']} - {request.form.get('ie')}
            {cacheData[0]['im']} - {request.form.get('im')}
        """)

        if cacheData[0]['razao']!=request.form.get('razao') or cacheData[0]['cnpj']!=request.form.get('cnpj') or cacheData[0]['cidade']!=request.form.get('cidade') or cacheData[0]['modalidade']!=str(request.form.get('regime')).upper() or request.form.get('ie')!=cacheData[0]['ie'] or request.form.get('im')!=cacheData[0]['im']:
            if cacheData[0]['modalidade']=='SIMPLES ME':
                db.RequestDB('').requestCommitOtimized("UPDATE EnterpriseSimplesNacional SET razao=?, cnpj=?, cidade=?, modalidade=?, ie=?, im=? WHERE id=?", (request.form.get('razao'),request.form.get('cnpj'),request.form.get('cidade'),request.form.get('regime'),request.form.get('ie'),request.form.get('im'), id))
            
            elif cacheData[0]['modalidade']=='LUCRO PRESUMIDO':
                db.RequestDB('').requestCommitOtimized("UPDATE EnterpriseLucroPresumido SET razao=?, cnpj=?, cidade=?, modalidade=?, ie=?, im=? WHERE id=? ", (request.form.get('razao'),request.form.get('cnpj'),request.form.get('cidade'),request.form.get('regime'),request.form.get('ie'),request.form.get('im'), id))
            
            else:
                return jsonify('Error regime não informado')
        return jsonify(f'Request Put: {cacheData}')
    else:
        return pageNotFound('')

#efetua o cadastro de uma empresa
@app.route('/page/requestRegister', methods=['POST'])
def registerCompany():
    if request.method=='POST':
        print(len(request.form.get('cnpj')))
        if request.form.get('regime')=='simples me' and len(request.form.get('cnpj'))==14:
            db.RequestDB('').requestCommitOtimized("INSERT INTO EnterpriseSimplesNacional (codigo, razao, cnpj, cidade, modalidade, ie) VALUES (?,?,?,?,?,?)",(f'{request.form.get('codigo')}', f'{request.form.get('razao')}', f'{request.form.get('cnpj')[:2]}.{request.form.get('cnpj')[2:5]}.{request.form.get('cnpj')[5:8]}/{request.form.get('cnpj')[8:12]}-{request.form.get('cnpj')[12:]}', f'{request.form.get('cidade')}', str(request.form.get('regime')).upper(),f'{request.form.get('ie')}'))
            try:
                data = db.RequestDB('').getData(f"SELECT * FROM EnterpriseSimplesNacional ORDER BY id DESC LIMIT 1", request.remote_addr)
                if data[0]['razao']==request.form.get('razao'):
                    print(data[0]['id'])
                    return redirect(url_for('requestFrontData', id=data[0]['id'], modalidade='SimplesNacional'))
                else:
                    return jsonify('Erro')
            except:
                return pageNotFound('')
        else:
            return jsonify('Erro register company ')

#efetua a exclusão de uma empresa
@app.route('/page/deleting/<id>/<modal>')
def requestDel(id, modal):
    if modal=='SIMPLES ME':
        db.RequestDB('').DelFile(id, modal)
        return redirect(url_for('requestGetSN'))
    elif modal=='LUCRO PRESUMIDO':
        db.RequestDB('').DelFile(id, modal)
        return redirect(url_for('requestGetLP'))
    else:
        return pageNotFound('')

if __name__=='__main__':
    app.run(debug=True)