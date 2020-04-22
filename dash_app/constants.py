countries = ['Italy']

translation_it = {'ricoverati_con_sintomi':'hospitalized_with_symptoms',
                  'terapia_intensiva': 'intensive_care',
                  'totale_ospedalizzati':'total_hospitalized',
                  'isolamento_domiciliare': 'home_isolation',
                  'totale_positivi':'total_positive',
                  'dimessi_guariti':'recovered_discharged',
                  'deceduti':'deaths',
                  'totale_casi':'total_cases',
                  'tamponi':'tests',
                  'casi_testati':'people_tested'}

translation_dict = {'Italy':translation_it}


urls = {'Italy':{'Nation':'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv',
              'Region': 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv',
              'Province':'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv'}
     }