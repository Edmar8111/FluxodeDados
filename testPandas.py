import pandas as pd
import requests

class requestFun:
    def __init__(self,listValue):
        #só executa a verificação do xlsx
        self.listValue=[]
        dictRefined=dict()
        content=pd.read_excel('Controle Contábil Geral 2025 - 13.02.2025.xlsx')
        listaCnpj=[a for a in content['CNPJ/CPF/CAEPF']]
        listaCidade=[a for a in content['Municipio - Estado']]
        for a in range(len(listaCidade)):
            dictRefined[f'{a}']=[f'{listaCidade[a]}',f'{listaCnpj[a]}']
        for a in dictRefined:
            if dictRefined[f'{a}'][0]=='CUIABÁ-MT':
                self.listValue.append(dictRefined[f'{a}'][1])
        return None
    
    def getFile(self, endpoint):
        return self.listValue

request=requestFun(list())

archiveGeral=pd.DataFrame({'NCM':[a for a in pd.read_excel('tipi.xlsx')['Unnamed: 0']],'ALIQUOTA':[a for a in pd.read_excel('tipi.xlsx')['Unnamed: 3']]})
print(archiveGeral)