response=requests.get('https://servicodados.ibge.gov.br/api/v2/cnae/subclasses').json()
with open('cnaes.json', 'r', encoding='utf-8') as file:
    data=json.load(file)
for a in range(len(response)):
    lista.append(response[a]['id'])
print(len(lista))
print(lista[1010:1020])
