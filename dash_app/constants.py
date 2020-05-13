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




table_cols = ['Legend','Tab','Data','Field 1','Field 2','Variable','Denominator']#,'Visible (on/off)']#,'Lin/Log','Var/Cum']

google_dtype = {'sub_region_2':str,
                'retail_and_recreation_percent_change_from_baseline':float,
                'grocery_and_pharmacy_percent_change_from_baseline':float,
                'parks_percent_change_from_baseline':float,
                'transit_stations_percent_change_from_baseline':float,
                'workplaces_percent_change_from_baseline':float,
                'residential_percent_change_from_baseline':float,
}