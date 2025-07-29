
#passar para refatoramento
endereco={'emitente':{'logradouro':'','numero':''},'destinatario':{'logradouro':'','numero':''}}

#inicio de verificação
query_acesso=soup.find_all('td') #soup* acesso ao arquivo diretamente
exec_=[]

for i in query_acesso:
    if i.text[:8]=='Endereço':
        refinamento=str(i.text[8:]).strip().replace('\n','')
        tag_busca=refinamento.find(',')
        exec_.append(0)
        try:
            #verifica se contem complemento
            print(f'{len(exec_)}ª execução')
            refinamento_0=str(refinamento[tag_busca+1:]).replace(' ','')
            refinamento_0=re.sub(r'[^a-zA-Z0-9]','',str(refinamento_0[tag_busca+1:]))

            v=1 if len(refinamento_0)>0 else 0
            if len(exec_)==1 and v==1 and endereco['emitente']['complemento']=='':
                print('alocação emitente') 
                endereco['emitente']['complemento']=refinamento_0
                print(f'resultado:{refinamento_0}')
            if len(exec_)>1 and v==1:
                print('alocação destinatario')
                endereco['destinatario']['complemento']=refinamento_0
                print(f'resultado:{refinamento_0}')
        except:
            pass
        if len(exec_)==2:
            endereco['destinatario']['logradouro']=str(refinamento[:tag_busca])
            endereco['destinatario']['numero']=re.sub(r'\D','',refinamento[tag_busca:])
        if len(exec_)==1:
            endereco['emitente']['logradouro']=str(refinamento[:tag_busca])
            endereco['emitente']['numero']=re.sub(r'\D','',refinamento[tag_busca:])
        
        
        refinamento=refinamento.replace(',','')
               
        #endereco.append['logradouro'](refinamento[:tag_busca])
        #refinamento=refinamento.replace(' ','')
        refinamento=refinamento.replace('s/n','')

