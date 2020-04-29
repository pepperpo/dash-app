import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import time
import dash_html_components as html

def generate_plot(dash_session_in,sel_reg_dropdown,aggr_in,log_in):

    fig = go.Figure()
    fig.update_layout( margin={'t': 0})

    fig_data = []
    annot_flag = [False]

    t1 = time.time()

    messages = []

    for cur_row in sel_reg_dropdown:

        if cur_row['Tab']=='health':
            dash_session = dash_session_in[cur_row['Data']][cur_row['Area type']]
            cur_area = cur_row['Area']
            #aggr_in = cur_row['Var/Cum']
            #log_in = cur_row['Lin/Log']
            norm_in = cur_row['Denominator']
            col_in = cur_row['Variable']
            legend = cur_row['Legend']

            df = pd.DataFrame(dash_session['data'])
            if dash_session['loc']:
                cur_idx = df[dash_session['loc']] == cur_area
                df = df.loc[cur_idx]

            valid_flag = plot_df(df,fig_data,aggr_in,col_in,norm_in,log_in,legend)
            if valid_flag==False:
                messages.append(html.P('Trace {} could not be plotted because log of negative value'.format(legend)))

    fig = go.Figure(data=fig_data)

    # Change the bar mode
    if log_in=='lin':
        log_in = 'linear'
    fig.update_layout(hovermode='x unified',yaxis_type=log_in,margin={'t': 0},legend_orientation="h",showlegend=True,legend_title_text='Legend: ')

    return fig,messages


def plot_df(df,fig_data,aggr_in,cur_col,norm_in,log_in,legend):
    date = df['date'].dt.date

    if norm_in:
        if aggr_in == 'cum':
            denom = df[norm_in]
        else:
            denom = df[norm_in].diff()  # np.concatenate([[1], df[norm_in].diff()])
    else:
        denom = 1.


    if aggr_in == 'cum':
        numer = df[cur_col]
    else:
        numer = df[cur_col].diff()  # np.concatenate([[0],df[cur_col].diff()])

    # fig_data.append(go.Bar(name=cur_col, x=date, y=numer/denom))

    y_val = numer / denom

    if not (np.any(y_val < 0) and log_in == 'log'):
        fig_data.append(go.Scatter(name='{}'.format(legend), x=date, y=y_val, mode='lines+markers'))
        valid_flag = True
    else:
        valid_flag = False
    return valid_flag



def load_data(all_data_dict,filesize_dict):

    from constants import translation_dict
    import numpy as np

    fs_key = 'Mobility_Apple'
    if filesize_dict[fs_key]['is_new'] or not all_data_dict:
        cur_df = pd.read_csv(
            filesize_dict[fs_key]['f_path'],
            header=0)
        all_data_dict[fs_key] = cur_df
        filesize_dict[fs_key]['is_new'] = False

    fs_key = 'Mobility_Google'
    if filesize_dict[fs_key]['is_new'] or not all_data_dict:
        cur_df = pd.read_csv(
            filesize_dict[fs_key]['f_path'],
            header=0,dtype={'sub_region_2':str})
        all_data_dict[fs_key] = cur_df
        filesize_dict[fs_key]['is_new'] = False

    fs_key = 'Response_Oxford'
    if (filesize_dict[fs_key]['is_new'] or not all_data_dict):
        cur_df = pd.read_csv(
            filesize_dict[fs_key]['f_path'],
            header=0,converters={'Date':pd.to_datetime})
        all_data_dict[fs_key] = cur_df
        filesize_dict[fs_key]['is_new'] = False


    countries = all_data_dict['Response_Oxford']['CountryName'].unique().tolist()

    for country_in in countries:
        if country_in == 'Italy':
            fs_key = '{}_Nation'.format(country_in)
            fs_key_region = '{}_Region'.format(country_in)
            fs_key_province = '{}_Province'.format(country_in)
            if filesize_dict[fs_key]['is_new'] or not all_data_dict:

                cur_tr = translation_dict[country_in]

                df_nation = pd.read_csv(
                    filesize_dict[fs_key]['f_path'],
                    header=0,converters={'data':pd.to_datetime})
                df_region = pd.read_csv(
                    filesize_dict[fs_key_region]['f_path'],
                    header=0,converters={'data':pd.to_datetime})
                df_province = pd.read_csv(
                    filesize_dict[fs_key_province]['f_path'],
                    header=0,converters={'data':pd.to_datetime})

                options_nation_region_it = ['ricoverati_con_sintomi','terapia_intensiva','totale_ospedalizzati','isolamento_domiciliare','totale_positivi','dimessi_guariti','deceduti','totale_casi','tamponi','casi_testati']
                options_province_it = ['totale_casi']

                #apply translations
                options_nation_region = [cur_tr[cur_var] for cur_var in options_nation_region_it]
                options_province = [cur_tr[cur_var] for cur_var in options_province_it]
                df_nation.rename(columns=cur_tr, inplace=True)
                df_region.rename(columns=cur_tr, inplace=True)
                df_province.rename(columns=cur_tr, inplace=True)

                region_list = sorted(df_region['denominazione_regione'].unique().tolist())
                province_list = sorted(df_province['denominazione_provincia'].unique().tolist())
                province_list.remove('In fase di definizione/aggiornamento')

                data = {'Country':  {'data':df_nation,  'options':options_nation_region,'norm':options_nation_region,'cols':['Italy'],'loc':None},
                        'Region':   {'data':df_region,  'options':options_nation_region,'norm':options_nation_region,'cols':region_list,'loc':'denominazione_regione'},
                        'Province': {'data':df_province,'options':options_province,     'norm':[]                   ,'cols':province_list,'loc':'denominazione_provincia'}}

                all_data_dict[country_in] = data
                filesize_dict[fs_key]['is_new'] = False
        else:
            cur_tr = translation_dict['Response_Oxford']
            health_cols = ['Date','CountryName','ConfirmedCases','ConfirmedDeaths']
            health_opts = [cur_tr[cur_var] for cur_var in health_cols[2:]]
            df_nation = all_data_dict['Response_Oxford'].loc[:,health_cols]
            df_nation.rename(columns=cur_tr, inplace=True)
            data = {'Country': {'data': df_nation, 'options': health_opts, 'norm': health_opts,'cols': [country_in],'loc':'CountryName'}}
            all_data_dict[country_in] = data


def save_data(data_dir,filesize_dict):
    from constants import urls
    import requests
    import os
    import json
    from urllib.parse import urlparse

    for key1, value1 in urls.items():
        for key2, value2 in value1.items():

            if key2=='Apple':
                #https://towardsdatascience.com/empowering-apple-mobility-trends-reports-with-bigquery-and-data-studio-1b188ab1c612
                response = requests.head(value2, allow_redirects=True)
                if response.status_code==200:
                    r_apple = requests.get(value2)
                    d_apple = json.loads(r_apple.text)
                    url_name = 'https://covid19-static.cdn-apple.com{}{}'.format(d_apple['basePath'],d_apple['regions']['en-us']['csvPath'])
                else:
                    url_name = None
            else:
                url_name = value2

            if url_name:
                fname = '{}_{}'.format(key1,key2)
                response = requests.head(url_name, allow_redirects=True)
                size = response.headers.get('content-length', 0)
                status_code = response.status_code

                #print(key2,status_code,size)
                url_path = urlparse(url_name).path
                extension = os.path.splitext(url_path)[1]
                file_path = os.path.join(data_dir, fname + extension)

                #reload_flag = (fname not in filesize_dict) or size > filesize_dict[fname]['size'] or not os.path.exists(file_path)
                reload_flag = (fname not in filesize_dict) or not os.path.exists(file_path)

                if status_code==200 and reload_flag:
                    myFile = requests.get(url_name)
                    open(file_path, 'wb').write(myFile.content)
                    filesize_dict[fname]={'size':size,'is_new':True,'f_path':file_path}


def data2dropdown(country_in,area_type,dict_in):
    list_in = dict_in[country_in][area_type]['cols']
    drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in list_in]
    return drp


def set_regions_options(country_in,region_st,val_st,is_province):
    if is_province:
        suffix = 'P'
    else:
        suffix = 'R'
    ret = [{'label': cur_item, 'value': '{}_{}_{}'.format(country_in,suffix,cur_item)} for cur_item in region_st if
     '{}_{}_{}'.format(country_in,suffix,cur_item) not in val_st]
    return ret

def get_regions_options(str_in):
    import re
    m = re.search('(.+)_([PR])_(.+)', str_in)
    if m:
        country = m.group(1)
        p_flag = m.group(2)
        region_name = m.group(3)
    else:
        country, p_flag, region_name = 'a', 'a', 'a'
    return [country, p_flag, region_name]

if __name__ == "__main__":
    generate_plot('Italy')




# if annot_flag[0] is True:
    #     annotations = [
    #         dict(
    #             x=0.5,
    #             y=0.1,
    #             showarrow=False,
    #             text="Some variables were deleted because log of a negative value",
    #             xref="paper",
    #             yref="paper"
    #         )]
    # else:
    #     annotations = []