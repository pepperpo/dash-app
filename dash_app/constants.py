#countries = ['Italy']

translation_it = {'ricoverati_con_sintomi':'hospitalized_with_symptoms',
                  'terapia_intensiva': 'intensive_care',
                  'totale_ospedalizzati':'total_hospitalized',
                  'isolamento_domiciliare': 'home_isolation',
                  'totale_positivi':'total_positive',
                  'dimessi_guariti':'recovered_discharged',
                  'deceduti':'deaths',
                  'totale_casi':'total_cases',
                  'tamponi':'tests',
                  'casi_testati':'people_tested',
                  'data':'date'}

translation_ox = {'Date':'date',
                  'ConfirmedCases': 'total_cases',
                  'ConfirmedDeaths':'deaths'}

translation_dict = {'Italy':translation_it,'Response_Oxford':translation_ox}


urls = {'Italy':    {'Nation'  :'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv',
                     'Region'  : 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv',
                     'Province':'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv'},
        'Mobility': {'Apple'   :'https://covid19-static.cdn-apple.com/covid19-mobility-data/current/v1/index.json',
                     'Google'  :'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'},
        'Response': {'Oxford'  :'https://github.com/OxCGRT/covid-policy-tracker/raw/master/data/OxCGRT_latest.csv'}
     }

table_cols = ['Legend','Tab','Data','Area','Area type','Variable','Denominator']#,'Lin/Log','Var/Cum']