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
valores_tmp_hr0 = {'data':[],'tmp':[]}
cidade_input = ''
#conversor para data atual e consequentemente para demais dias criando verificação para implementar
def prev_dias(cidade):
    requisitar_dados = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key=4e089e5d392043b992d174228240412&q={cidade}&days=7&aqi=yes')
    if requisitar_dados.status_code==200:
        dados_api = requisitar_dados.json()
        print(f'Lat:{dados_api['location']['lat']} Long:{dados_api['location']['lon']}')
        if len(lista_diario['cidade'])>0:
            lista_diario['cidade'].pop()
            lista_diario['region'].pop()
            lista_diario['temp'].pop()
            lista_diario['humidity'].pop()
            lista_diario['sensa_term'].pop()
            lista_diario['icon'].pop()
        if len(lista_total['tmp_max'])>0:
                lista_total['tmp_max']=[]
                lista_total['tmp_min']=[]
                lista_total['preci_probabilidade']=[]
        if len(valores_tmp_hr0['data'])>0:
            valores_tmp_hr0['data']=[]
            valores_tmp_hr0['tmp']=[]
            
                

        lista_diario['cidade'].append(dados_api['location']['name'])
        lista_diario['region'].append(dados_api['location']['region'])
        #requisição diaria
        lista_diario['temp'].append(dados_api['current']['temp_c'])
        lista_total['tmp_max'].append(dados_api['forecast']['forecastday'][0]['day']['maxtemp_c'])
        lista_total['tmp_min'].append(dados_api['forecast']['forecastday'][0]['day']['mintemp_c'])
        lista_diario['humidity'].append(dados_api['current']['humidity'])
        lista_diario['sensa_term'].append(dados_api['current']['feelslike_c'])
        lista_diario['icon'].append(dados_api['current']['condition']['icon']) 
        lista_total['icone'].append(dados_api['forecast']['forecastday'][0]['day']['condition']['icon'])
        lista_total['icone'].append(dados_api['forecast']['forecastday'][1]['day']['condition']['icon'])
        
        if ' ' in str(lista_diario['cidade'][0]):
            valor = str(lista_diario['cidade'][0]).replace(' ', '_')
            lista_diario['cidade'][0] = valor
        requisitar_dados0 = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={dados_api['location']['lat']}&longitude={dados_api['location']['lon']}&current=relative_humidity_2m&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,precipitation_probability_max&timezone=auto')
        if requisitar_dados0.status_code==200:
            dados_api0 = requisitar_dados0.json()    
            print('Codigo executado')
            #lista_total['preci_probabilidade'].append(dados_api0['daily']['precipitation_probability_max'][0])
            for a in range(0, 7):
                lista_total['tmp_max'].append(dados_api0['daily']['temperature_2m_max'][a])
                lista_total['tmp_min'].append(dados_api0['daily']['temperature_2m_min'][a])
                lista_total['preci_probabilidade'].append(dados_api0['daily']['precipitation_probability_max'][a])    
            for b in range(dt.datetime.now().hour, len(dados_api0['hourly']['time'])):
                valores_tmp_hr0['data'].append(str(dados_api0['hourly']['time'][b])[11:])
                valores_tmp_hr0['tmp'].append(dados_api0['hourly']['temperature_2m'][b])
            
            print(f'Lista {valores_tmp_hr0['tmp']}')

            
         
# Create your views here.
def home0(request):
    if request.method == 'GET':
        print('Requisição Get')
        return render(request, 'base.html')
    if request.method=='POST':
        prev_dias(str(request.POST.get('cidade_input')))
        if '_' in str(lista_diario['cidade'][0]):
            valor = str(lista_diario['cidade'][0]).replace('_', ' ')
            lista_diario['cidade'][0] = valor
        
        return render(request, 'base.html', {'city':lista_diario['cidade'][0]+',','region':lista_diario['region'][0],
                                             'temperatura':lista_diario['temp'][0],'tmp_max':lista_total['tmp_max'][0],'tmp_min':lista_total['tmp_min'][0],
                                             'windchill':lista_diario['sensa_term'][0], 'humidity':lista_diario['humidity'][0], 
                                             'preci_probabilidade':str(lista_total['preci_probabilidade'][0])+'%',
                                             'icon_ref':lista_diario['icon'][0],

                                             'tmp_max0':lista_total['tmp_max'][1],'tmp_min0':lista_total['tmp_min'][1],'icon_tmp0':lista_total['icone'][0],
                                             'preci_prev0':str(lista_total['preci_probabilidade'][1])+'%','data0':datas_homologadas[0],
                                             
                                             'tmp_max1':lista_total['tmp_max'][2],'tmp_min1':lista_total['tmp_min'][2],'icon_tmp1':lista_total['icone'][1],
                                             'preci_prev1':str(lista_total['preci_probabilidade'][2])+'%','data1':datas_homologadas[1],
                                             
                                             'tmp_max2':lista_total['tmp_max'][3],'tmp_min2':lista_total['tmp_min'][3],
                                             'preci_prev2':str(lista_total['preci_probabilidade'][3])+'%','data2':datas_homologadas[2],
                                             
                                             'tmp_max3':lista_total['tmp_max'][4],'tmp_min3':lista_total['tmp_min'][4],
                                             'preci_prev3':str(lista_total['preci_probabilidade'][4])+'%','data3':datas_homologadas[3],
                                             
                                             'tmp_max4':lista_total['tmp_max'][5],'tmp_min4':lista_total['tmp_min'][5],
                                             'preci_prev4':str(lista_total['preci_probabilidade'][5])+'%','data4':datas_homologadas[4],
                                             
                                             'tmp_max5':lista_total['tmp_max'][6],'tmp_min5':lista_total['tmp_min'][6],
                                             'preci_prev5':str(lista_total['preci_probabilidade'][6])+'%','data5':datas_homologadas[5],
                                             })
    
def grafico(request):
    global valores_tmp_hr0
    valores_tmp_hr={'data':[],'tmp':[]}
    lista_grafico=[]
    for a in range(0, len(lista_total['tmp_max'])):
        lista_grafico.append(lista_total['tmp_max'][a]*5)
    for b in range(0, len(valores_tmp_hr0['tmp'])):
        valores_tmp_hr['data'].append(valores_tmp_hr0['data'][b])
        valores_tmp_hr['tmp'].append(valores_tmp_hr0['tmp'][b]*5)
    
    return render(request, 'grafico.html', {'data0':datas_homologadas[0],'padding_valor0':lista_grafico[1],'data1':datas_homologadas[1],'padding_valor1':lista_grafico[2]
                                            ,'data2':datas_homologadas[2],'padding_valor2':lista_grafico[3],'data3':datas_homologadas[3],'padding_valor3':lista_grafico[4],
                                            'data4':datas_homologadas[4],'padding_valor4':lista_grafico[5],'data5':datas_homologadas[5],'padding_valor5':lista_grafico[6],
                                            
                                            'tmp_0':valores_tmp_hr0['tmp'][0],'tmp_1':valores_tmp_hr0['tmp'][1],'tmp_2':valores_tmp_hr0['tmp'][2],'tmp_3':valores_tmp_hr0['tmp'][3],
                                            'tmp_4':valores_tmp_hr0['tmp'][4],'tmp_5':valores_tmp_hr0['tmp'][5],'tmp_6':valores_tmp_hr0['tmp'][6],'tmp_7':valores_tmp_hr0['tmp'][7],
                                            'tmp_8':valores_tmp_hr0['tmp'][8],'tmp_9':valores_tmp_hr0['tmp'][9],'tmp_00':valores_tmp_hr0['tmp'][10],'tmp_01':valores_tmp_hr0['tmp'][11],
                                            'tmp_02':valores_tmp_hr0['tmp'][12],'tmp_03':valores_tmp_hr0['tmp'][13],'tmp_04':valores_tmp_hr0['tmp'][14],'tmp_05':valores_tmp_hr0['tmp'][15],
                                            'tmp_06':valores_tmp_hr0['tmp'][16],'tmp_07':valores_tmp_hr0['tmp'][17],'tmp_08':valores_tmp_hr0['tmp'][18],'tmp_09':valores_tmp_hr0['tmp'][19],
                                            'tmp_10':valores_tmp_hr0['tmp'][20],'tmp_11':valores_tmp_hr0['tmp'][21],'tmp_12':valores_tmp_hr0['tmp'][22],'tmp_13':valores_tmp_hr0['tmp'][23],
                                            'data_0':valores_tmp_hr['data'][0],'padding_valor_0':valores_tmp_hr['tmp'][0],'data_1':valores_tmp_hr['data'][1],'padding_valor_1':valores_tmp_hr['tmp'][1],
                                            'data_2':valores_tmp_hr['data'][2],'padding_valor_2':valores_tmp_hr['tmp'][2],'data_3':valores_tmp_hr['data'][3],'padding_valor_3':valores_tmp_hr['tmp'][3],
                                            'data_4':valores_tmp_hr['data'][4],'padding_valor_4':valores_tmp_hr['tmp'][4],'data_5':valores_tmp_hr['data'][5],'padding_valor_5':valores_tmp_hr['tmp'][5],
                                            'data_6':valores_tmp_hr['data'][6],'padding_valor_0':valores_tmp_hr['tmp'][6],'data_7':valores_tmp_hr['data'][7],'padding_valor_01':valores_tmp_hr['tmp'][7],
                                            'data_8':valores_tmp_hr['data'][8],'padding_valor_02':valores_tmp_hr['tmp'][8],'data_9':valores_tmp_hr['data'][9],'padding_valor_03':valores_tmp_hr['tmp'][9],
                                            'data_00':valores_tmp_hr['data'][10],'padding_valor_04':valores_tmp_hr['tmp'][10],'data_01':valores_tmp_hr['data'][11],'padding_valor_05':valores_tmp_hr['tmp'][11],
                                            'data_02':valores_tmp_hr['data'][12],'padding_valor_06':valores_tmp_hr['tmp'][12],'data_03':valores_tmp_hr['data'][13],'padding_valor_07':valores_tmp_hr['tmp'][13],
                                            'data_04':valores_tmp_hr['data'][14],'padding_valor_08':valores_tmp_hr['tmp'][14],'data_05':valores_tmp_hr['data'][15],'padding_valor_09':valores_tmp_hr['tmp'][15],
                                            'data_06':valores_tmp_hr['data'][16],'padding_valor_10':valores_tmp_hr['tmp'][16],'data_07':valores_tmp_hr['data'][17],'padding_valor_11':valores_tmp_hr['tmp'][17],
                                            'data_08':valores_tmp_hr['data'][18],'padding_valor_12':valores_tmp_hr['tmp'][18],'data_09':valores_tmp_hr['data'][19],'padding_valor_13':valores_tmp_hr['tmp'][19],
                                            'data_10':valores_tmp_hr['data'][20],'padding_valor_14':valores_tmp_hr['tmp'][20],'data_11':valores_tmp_hr['data'][21],'padding_valor_15':valores_tmp_hr['tmp'][21],
                                            'data_12':valores_tmp_hr['data'][22],'padding_valor_16':valores_tmp_hr['tmp'][22],'data_13':valores_tmp_hr['data'][23],'padding_valor_17':valores_tmp_hr['tmp'][23]


                                            })