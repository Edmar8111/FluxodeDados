from django.http import HttpResponse
from django.shortcuts import render
import requests
import datetime as dt

# https://api.weatherapi.com/v1/forecast.json?key=5c39e50cba4a4a4fa3530609242011&q=cuiaba&days=7&aqi=yes

datas_homologadas=[]
data_atual = dt.datetime.today()
for a in range(1, 7):
    data_atual = data_atual.replace(day=data_atual.day+1)
    datas_homologadas.append(data_atual.strftime('%d/%m/%y'))

lista_total = {'tmp_max':[], 'tmp_min':[],'humidity':[],'preci_probabilidade':[],
               'icone':[],
               }
lista_diario = {'temp':[],'cidade':[],'region':[],'sensa_term':[],'humidity':[],'icon':[]}

#conversor para data atual e consequentemente para demais dias criando verificação para implementar
def prev_dias(cidade):
    requisitar_dados = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key=4e089e5d392043b992d174228240412&q={cidade}&days=7&aqi=yes')
    if requisitar_dados.status_code==200:
        dados_api = requisitar_dados.json()
        requisitar_dados0 = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude=-10&longitude=-55&current=relative_humidity_2m&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,precipitation_probability_max&timezone=America%2F{dados_api['location']['name']}')
        if requisitar_dados0.status_code==200:
            dados_api0 = requisitar_dados0.json()

            print(dados_api0['daily']['temperature_2m_max'])
            #requisição diaria
            lista_diario['cidade'].append(dados_api['location']['name'])
            lista_diario['region'].append(dados_api['location']['region'])
            lista_diario['temp'].append(dados_api['current']['temp_c'])
            lista_diario['humidity'].append(dados_api['current']['humidity'])
            lista_diario['sensa_term'].append(dados_api['current']['feelslike_c'])
            lista_diario['icon'].append(dados_api['current']['condition']['icon'])
            
            lista_total['icone'].append(dados_api['forecast']['forecastday'][0]['day']['condition']['icon'])
            lista_total['icone'].append(dados_api['forecast']['forecastday'][1]['day']['condition']['icon'])
            
            for a in range(0, 7):
                lista_total['tmp_max'].append(dados_api0['daily']['temperature_2m_max'][a])
                lista_total['tmp_min'].append(dados_api0['daily']['temperature_2m_min'][a])
                lista_total['preci_probabilidade'].append(dados_api0['daily']['precipitation_probability_max'][a])
            print(lista_total)
        print('Codigo executado')
        

         
# Create your views here.
def home0(request):
    if request.method == 'GET':
        print('Requisição Get')
        return render(request, 'base.html')
    if request.method=='POST':
        print(str(request.POST.get('cidade_input')))
        prev_dias(str(request.POST.get('cidade_input')))
        print(lista_total)
        print(datas_homologadas)
        return render(request, 'base.html', {'city':lista_diario['cidade'][0],'region':lista_diario['region'][0],
                                             'temperatura':lista_diario['temp'][0],'tmp_max':lista_total['tmp_max'][0],'tmp_min':lista_total['tmp_min'][0],
                                             'windchill':lista_diario['sensa_term'][0], 'humidity':lista_diario['humidity'][0], 
                                             'preci_probabilidade':str(lista_total['preci_probabilidade'][0])+'%',
                                             'icon_ref':lista_diario['icon'][0],

                                             'tmp_max0':lista_total['tmp_max'][1],'tmp_min0':lista_total['tmp_min'][1],'icon_tmp0':lista_total['icone'][0],
                                             'preci_prev0':str(lista_total['preci_probabilidade'][1])+'%','data0':datas_homologadas[0],
                                             
                                             'tmp_max1':lista_total['tmp_max'][2],'tmp_min1':lista_total['tmp_min'][2],'icon_tmp1':lista_total['icone'][1],
                                             'preci_prev1':str(lista_total['preci_probabilidade'][2])+'%','data1':datas_homologadas[1],
                                             
                                            #  'tmp_max2':lista_total['tmp_max'][3],'tmp_min2':lista_total['tmp_min'][3],'humidity_prev2':lista_total['humidity'][3],
                                            #  'preci_prev2':str(lista_total['preci_probabilidade'][3])+'%','data2':datas_homologadas[2],'icon_tmp2':lista_total['icone'][3],
                                             
                                            #  'tmp_max3':lista_total['tmp_max'][4],'tmp_min3':lista_total['tmp_min'][4],'humidity_prev3':lista_total['humidity'][4],
                                            #  'preci_prev3':str(lista_total['preci_probabilidade'][4])+'%','data3':datas_homologadas[3],'icon_tmp3':lista_total['icone'][4],
                                             
                                            #  'tmp_max4':lista_total['tmp_max'][5],'tmp_min4':lista_total['tmp_min'][5],'humidity_prev4':lista_total['humidity'][5],
                                            #  'preci_prev4':str(lista_total['preci_probabilidade'][5])+'%','data4':datas_homologadas[4],'icon_tmp4':lista_total['icone'][5],
                                             
                                            #  'tmp_max5':lista_total['tmp_max'][6],'tmp_min5':lista_total['tmp_min'][6],'humidity_prev5':lista_total['humidity'][6],
                                            #  'preci_prev5':str(lista_total['preci_probabilidade'][6])+'%','data5':datas_homologadas[5],'icon_tmp5':lista_total['icone'][6],
                                             })