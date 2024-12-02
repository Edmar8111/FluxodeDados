from django.http import HttpResponse
from django.shortcuts import render
import requests
import datetime as dt

# https://api.weatherapi.com/v1/forecast.json?key=5c39e50cba4a4a4fa3530609242011&q=cuiaba&days=7&aqi=yes


#conversor para data atual e consequentemente para demais dias criando verificação para implementar
def prev_dias(cidade):
    requisitar_dados = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key=5c39e50cba4a4a4fa3530609242011&q={cidade}&days=7&aqi=yes')
    
    try:
        if requisitar_dados.status_code==200:
            dados_api = requisitar_dados.json()
        # print(dados_api['forecast']['forecastday'][0])
        for a in range(0, 7):
            print(dados_api['forecast']['forecastday'][a]['day']['maxtemp_c'])

        print('Codigo executado')
        data_atual = str(dt.datetime.today())
        
        print(f'Data:{data_atual[:10]}')
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
        print('Requisitando Post')
        return render(request, 'base.html')