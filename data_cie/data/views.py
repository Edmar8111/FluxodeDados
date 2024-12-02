from django.http import HttpResponse
from django.shortcuts import render
import requests
import datetime as dt

# https://api.weatherapi.com/v1/forecast.json?key=5c39e50cba4a4a4fa3530609242011&q=cuiaba&days=7&aqi=yes

datas_homologadas=[]
data_atual = dt.datetime.today()
for a in range(1, 7):
    data_atual = data_atual.replace(day=data_atual.day+a)
    datas_homologadas.append(data_atual.strftime('%d/%m/%y'))
print(datas_homologadas)
lista_total = {'tmp_max':[], 'tmp_min':[],'humidity':[],'preci_probabilidade':[],
               'icone':[],
               }
lista_diario = {'temp':[],'cidade':[],'region':[],'sensa_term':[],'humidity':[],'icon':[]}

#conversor para data atual e consequentemente para demais dias criando verificação para implementar
def prev_dias(cidade):
    requisitar_dados = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key=5c39e50cba4a4a4fa3530609242011&q={cidade}&days=7&aqi=yes')
    
    try:
        if requisitar_dados.status_code==200:
            dados_api = requisitar_dados.json()
        #requisição diaria
        lista_diario['cidade'].append(dados_api['location']['name'])
        lista_diario['region'].append(dados_api['location']['region'])
        lista_diario['temp'].append(dados_api['current']['temp_c'])
        lista_diario['humidity'].append(dados_api['current']['humidity'])
        lista_diario['sensa_term'].append(dados_api['current']['feelslike_c'])
        lista_diario['icon'].append(dados_api['current']['condition']['icon'])
        for a in range(0, 7):
            lista_total['tmp_max'].append(dados_api['forecast']['forecastday'][a]['day']['maxtemp_c'])
            lista_total['tmp_min'].append(dados_api['forecast']['forecastday'][a]['day']['mintemp_c'])
            lista_total['humidity'].append(dados_api['forecast']['forecastday'][a]['day']['avghumidity'])
            lista_total['preci_probabilidade'].append(dados_api['forecast']['forecastday'][a]['day']['daily_chance_of_rain'])
            lista_total['icone'].append(dados_api['forecast']['forecastday'][a]['day']['condition']['icon'])

        print('Codigo executado')
        

        return
    except requisitar_dados.status_code != 200:
        return 

# Create your views here.
def home0(request):
    if request.method == 'GET':
        print('Requisição Get')
        return render(request, 'base.html')
    if request.method=='POST':
        prev_dias(str(request.POST.get('cidade_input')))
        print(lista_total)
        return render(request, 'base.html', {'temperatura':lista_diario['temp'][0],'tmp_max':lista_total['tmp_max'][0],'tmp_min':lista_total['tmp_min'][0],
                                             'windchill':lista_diario['sensa_term'][0], 'humidity':lista_diario['humidity'][0], 
                                             'preci_probabilidade':str(lista_total['preci_probabilidade'][0])+'%',
                                             'icon_ref':lista_diario['icon'][0],
                                             'tmp_max0':lista_total['tmp_max'][1],'tmp_min0':lista_total['tmp_min'][1],
                                             })