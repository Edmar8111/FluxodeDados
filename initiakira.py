import xmltodict
import json
import os

caminhoFindFile=os.path.abspath('')

with open('ReadThis.xml', 'rb') as arquivo:
    fileRead=xmltodict.parse(arquivo)

requestNFe=fileRead['NotasFiscais']['NF-e']['InfNFe']
requestNFS=fileRead['NotasFiscais']['NFS-e']['InfNFS-e']
requestCTe=fileRead['NotasFiscais']['CT-e']['InfCte']



def requestXMLSInfo():
    global requestNFe, requestCTe, requestNFS
    print('Insira a requisição ao indice referente: [1]=>NFS [2]=>NFe [3]=>CTe') 
    selectedIndex=input('Select Index: ')
    try:
        if int(selectedIndex)==1:
            return f"""
            ID:debBUGInfoRequestFuture
            <==INFO REFERENTE A NFS-e(Nota Fiscal de Serviços Eletronicos)==>
            Prestador:{requestNFS['Prestador']['RazaoSocial']}
            CNPJ:{requestNFS['Prestador']['CNPJ']}
            Tomador:{requestNFS['Tomador']['Nome']}
            CPF:{requestNFS['Tomador']['CPF']}
            Serviços Prestados:{requestNFS['Servico']['Descricao']}
            Valor:{requestNFS['Servico']['ValorServicos']}
            ISS:{requestNFS['Servico']['ISS']}
            """
        if int(selectedIndex)==2:
            return f"""
        <==INFO REFERENTE A NF-e(Nota Fiscal Eletronica de Produtos)==>
        Emissor:{requestNFe['Emit']}
        Destinatario:{requestNFe['Dest']}
        DET=>
        Produto:{requestNFe['Det']['Prod']}
        ICMS Porcentual:{requestNFe['Det']['Imposto']['ICMS']['ICMS00']['pICMS']}
        ICMS Total:{requestNFe['Det']['Imposto']['ICMS']['ICMS00']['vICMS']}
        """
        if int(selectedIndex)==3:
            return f"""
                    <==INFO REFERENTE CT-e(Conhecimento de Transporte Eletronico)==>
                    
                    Emissor:{requestCTe['Emit']}
                    Reemissor:{requestCTe['Rem']}
                    Destinatario:{requestCTe['Dest']}
                    Carga Total:{requestCTe['InfCTeNorm']['InfCarga']['vCarga']}
                    Carga Predominante:{requestCTe['InfCTeNorm']['InfCarga']['proPred']}
                    KeyNFe:{requestCTe['InfCTeNorm']['InfDoc']['InfNFe']['chave']}
                    """    
    except:
        while str(selectedIndex)!='1'!='2'!='3':
            print('Index Not Found')
            print('Insira a requisição ao indice referente: [1]=>NFS [2]=>NFe [3]=>CTe')    
            selectedIndex=input('Select Index: ')
        if int(selectedIndex)==1:
            return f"""
            ID:debBUGInfoRequestFuture
            INFO REFERENTE A NFS-e(Nota Fiscal de Serviços Eletronicos)==>
            Prestador:{requestNFS['Prestador']['RazaoSocial']}
            CNPJ:{requestNFS['Prestador']['CNPJ']}
            Tomador:{requestNFS['Tomador']['Nome']}
            CPF:{requestNFS['Tomador']['CPF']}
            Serviços Prestados:{requestNFS['Servico']['Descricao']}
            Valor:{requestNFS['Servico']['ValorServicos']}
            ISS:{requestNFS['Servico']['ISS']}
            """
        if int(selectedIndex)==2:
            return f"""
        INFO REFERENTE A NF-e(Nota Fiscal Eletronica de Produtos)==>
        Emissor:{requestNFe['Emit']}
        Destinatario:{requestNFe['Dest']}
        DET=>
        Produto:{requestNFe['Det']['Prod']}
        ICMS Porcentual:{requestNFe['Det']['Imposto']['ICMS']['ICMS00']['pICMS']}
        ICMS Total:{requestNFe['Det']['Imposto']['ICMS']['ICMS00']['vICMS']}
        """
        if int(selectedIndex)==3:
            return f"""
                    INFO REFERENTE CT-e(Conhecimento de Transporte Eletronico)
                    
                    Emissor:{requestCTe['Emit']}
                    Reemissor:{requestCTe['Rem']}
                    Destinatario:{requestCTe['Dest']}
                    Carga Total:{requestCTe['InfCTeNorm']['InfCarga']['vCarga']}
                    Carga Predominante:{requestCTe['InfCTeNorm']['InfCarga']['proPred']}
                    KeyNFe:{requestCTe['InfCTeNorm']['InfDoc']['InfNFe']['chave']}
                    """
    # print(f"""
        
    #     ID:debBUGInfoRequestFuture
    #     INFO REFERENTE A NFS-e(Nota Fiscal de Serviços Eletronicos)==>
    #     Prestador:{requestNFS['Prestador']['RazaoSocial']}
    #     CNPJ:{requestNFS['Prestador']['CNPJ']}
    #     Tomador:{requestNFS['Tomador']['Nome']}
    #     CPF:{requestNFS['Tomador']['CPF']}
    #     Serviços Prestados:{request['Servico']['Descricao']}
    #     Valor:{requestNFS['Servico']['ValorServicos']}
    #     ISS:{requestNFS['Servico']['ISS']}
    #     """)

    # print(f"""
    #     INFO REFERENTE A NF-e(Nota Fiscal Eletronica de Produtos)==>
    #     Emissor:{requestNFe['Emit']}
    #     Destinatario:{requestNFe['Dest']}
    #     DET=>
    #     Produto:{requestNFe['Det']['Prod']}
    #     ICMS Porcentual:{requestNFe['Det']['Imposto']['ICMS']['ICMS00']['pICMS']}
    #     ICMS Total:{requestNFe['Det']['Imposto']['ICMS']['ICMS00']['vICMS']}
    #     """)

    # print(f"""
    # INFO REFERENTE CT-e(Conhecimento de Transporte Eletronico)
    
    # Emissor:{requestCTe['Emit']}
    # Reemissor:{requestCTe['Rem']}
    # Destinatario:{requestCTe['Dest']}
    # Carga Total:{requestCTe['InfCTeNorm']['InfCarga']['vCarga']}
    # Carga Predominante:{requestCTe['InfCTeNorm']['InfCarga']['proPred']}
    # KeyNFe:{requestCTe['InfCTeNorm']['InfDoc']['InfNFe']['chave']}
    # """)
print(requestXMLSInfo())