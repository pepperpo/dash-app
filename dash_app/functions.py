import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import time
import dash_html_components as html
from plotly.subplots import make_subplots
import plotly.express as px

def generate_plot(data_dict,sel_reg_dropdown,aggr_in,log_in):

    fig = go.Figure()
    fig.update_layout( margin={'t': 40})
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig_data = []
    annot_flag = [False]

    t1 = time.time()

    messages = []

    appleFlag = False
    stFlag = False
    for cur_row in sel_reg_dropdown:
        cur_area = cur_row['Field 2']
        norm_in = cur_row['Denominator']
        col_in = cur_row['Variable']
        legend = cur_row['Legend']
        is_visible = 'on'#cur_row['Visible (on/off)']
        country_in = cur_row['Data']
        field_1 = cur_row['Field 1']
        if is_visible == 'on':
            if cur_row['Tab']=='health':
                dash_session = data_dict[country_in][field_1]
                df = pd.DataFrame(dash_session['data'])
                if dash_session['loc']:
                    cur_idx = df[dash_session['loc']] == cur_area
                    df = df.loc[cur_idx]

                cur_msg = plot_df(df,fig,aggr_in,col_in,norm_in,log_in,legend,False)
                if cur_msg:
                    messages.extend(cur_msg)

            if cur_row['Tab']=='response':
                if col_in == 'StringencyIndex':
                    stFlag = True
                df = data_dict['Response_Oxford']['df']
                cur_idx = df['CountryName'] == cur_area
                df = df.loc[cur_idx]
                plot_df(df, fig, 'cum', col_in, None, 'lin', legend,True)
                #messages.extend([html.Div('Testing2')])

            if cur_row['Tab'] == 'mobility - google':
                df = data_dict['Mobility_Google']['data']
                cur_idx=None
                if cur_area:
                    cur_idx = (df['country_region'] == country_in) & (df['sub_region_1'] == field_1) & (
                            df['sub_region_2'] == cur_area)
                elif field_1:
                    cur_idx = (df['country_region'] == country_in) & (df['sub_region_1'] == field_1) & (
                        pd.isnull(df['sub_region_2']))

                elif country_in:
                    cur_idx = (df['country_region'] == country_in) & (pd.isnull(df['sub_region_1'])) & (
                        pd.isnull(df['sub_region_2']))

                df = df.loc[cur_idx]
                plot_df(df, fig, 'cum', col_in, None, 'lin', legend, True)

            if cur_row['Tab'] == 'mobility - apple':
                df = data_dict['Mobility_Apple']['data']
                cur_idx = (df['geo_type'] == country_in) & (df['region'] == field_1) & (
                            df['transportation_type'] == col_in)

                if cur_idx.any():
                    df = df.loc[cur_idx].copy()
                    df = df.iloc[:, 4:].T
                    df.reset_index(inplace=True)
                    col_idx = df.columns.tolist()
                    col_idx.remove('index')
                    df.rename(columns={col_idx[0]: col_in, 'index': 'date'}, inplace=True)
                    df['date'] = pd.to_datetime(df['date'])
                    df[col_in] = df[col_in]-100.
                    plot_df(df, fig, 'cum', col_in, None, 'lin', legend, True)
                    appleFlag = True

    if appleFlag:
        cur_msg = [html.Div('Apple mobility traces are modified so that baseline is at 0% (in original data baseline is at 100%)')]
        messages.extend(cur_msg)

    if stFlag:
        annotations = [
            dict(
                x=0.01,
                y=1.,
                showarrow=False,
                text="Hover on the StringencyIndex to see more details",
                xref="paper",
                yref="paper"
            )]
    else:
        annotations = []


    #fig = go.Figure(data=fig_data)

    # Set y-axes titles
    fig.update_yaxes(title_text="health", secondary_y=False)
    fig.update_yaxes(title_text="response / mobility", secondary_y=True)

    # Change the bar mode
    if log_in=='lin':
        log_in = 'linear'

    #hovermode='x unified',
    fig.update_layout(yaxis_type=log_in,margin={'t': 40},legend_orientation="h",showlegend=True,legend_title_text='Legend (click on a marker to hide trace): ',annotations=annotations)

    return fig,messages


def plot_df(df,fig,aggr_in,cur_col,norm_in,log_in,legend,secondary_y):
    date = df['date'].dt.date

    denom = None
    if norm_in:
        if aggr_in == 'cum':
            denom = df[norm_in]
        else:
            denom = df[norm_in].diff()  # np.concatenate([[1], df[norm_in].diff()])

    if aggr_in == 'cum':
        numer = df[cur_col]
    else:
        numer = df[cur_col].diff()  # np.concatenate([[0],df[cur_col].diff()])

    # fig_data.append(go.Bar(name=cur_col, x=date, y=numer/denom))
    if denom:
        y_val = numer / denom
    else:
        y_val = numer

    cur_msg = []
    if not (np.any(y_val < 0) and log_in == 'log'):
        if cur_col=='StringencyIndex':
            add_txt = df['text']
        else:
            add_txt = None
        fig.add_trace(go.Scatter(name='{}'.format(legend), x=date, y=y_val, mode='lines+markers',text=add_txt),secondary_y=secondary_y)
    else:
        cur_msg = [html.Div('Trace {} could not be plotted because log of negative value'.format(legend))]
    #cur_msg = [html.Div('Testing')]
    return cur_msg



def load_data(all_data_dict,filesize_dict,app):

    from datetime import timedelta
    from constants import translation_dict,google_dtype
    import numpy as np

    fs_key = 'Mobility_Apple'
    if filesize_dict[fs_key]['is_new'] or not all_data_dict:
        app.server.logger.info('Refreshing {}'.format(fs_key))
        #app.server.logger.info('{}'.format(filesize_dict[fs_key]['f_path']))
        apple_df = pd.read_csv(
            filesize_dict[fs_key]['f_path'],
            header=0)

        geo_type_list = apple_df['geo_type'].unique().tolist()
        region_dict = {}
        for cur_geo in geo_type_list:
            cur_idx = apple_df['geo_type'] == cur_geo
            cur_df = apple_df.loc[cur_idx]
            region_list = cur_df['region'].unique().tolist()
            transportation_type = {}
            for cur_reg in region_list:
                cur_idx2 = cur_df['region'] == cur_reg
                cur_df2 = cur_df.loc[cur_idx2]
                transport_list = cur_df2['transportation_type'].unique().tolist()
                transportation_type[cur_reg] = transport_list
            region_dict[cur_geo] = transportation_type

        all_data_dict[fs_key] = {'options':region_dict,'data':apple_df}
        filesize_dict[fs_key]['is_new'] = False


    fs_key = 'Mobility_Google'
    if filesize_dict[fs_key]['is_new'] or not all_data_dict:
        app.server.logger.info('Refreshing {}'.format(fs_key))
        google_df = pd.read_csv(
            filesize_dict[fs_key]['f_path'],
            header=0,dtype=google_dtype,converters={'date':pd.to_datetime},keep_default_na=True)

        g_countries_l = google_df['country_region'].unique().tolist()
        g_options = {}
        for cur_country in g_countries_l:
            cur_idx = google_df['country_region'] == cur_country
            g_country_df = google_df.loc[cur_idx]
            g_sr1_l = g_country_df['sub_region_1'].unique().tolist()
            g_sr1_l = [x for x in g_sr1_l if not pd.isnull(x)]
            cur_dict = {}
            for cur_sr1 in g_sr1_l:
                cur_idx2 = g_country_df['sub_region_1'] == cur_sr1
                sr1_df = g_country_df.loc[cur_idx2]
                g_sr2_l = sr1_df['sub_region_2'].unique().tolist()
                g_sr2_l = [x for x in g_sr2_l if not pd.isnull(x)]
                cur_dict[cur_sr1] = g_sr2_l
            g_options[cur_country] = cur_dict

        col_names = google_df.columns.tolist()[5:]
        all_data_dict[fs_key] = {'options':g_options,'data':google_df,'col_names':col_names}

        filesize_dict[fs_key]['is_new'] = False

    fs_key = 'Response_Oxford'
    if (filesize_dict[fs_key]['is_new'] or not all_data_dict):
        app.server.logger.info('Refreshing {}'.format(fs_key))
        cur_df = pd.read_csv(
            filesize_dict[fs_key]['f_path'],
            header=0,converters={'Date':pd.to_datetime})
        cur_df['Date'] -= timedelta(days=1) #pd.to_datetime(cur_df['Date'])
        countries = cur_df['CountryName'].unique().tolist()
        col_names_f = cur_df.columns.tolist()[3:-4]
        if 'ConfirmedDeaths' in col_names_f:
            col_names_f.remove('ConfirmedDeaths')
        if 'ConfirmedCases' in col_names_f:
            col_names_f.remove('ConfirmedCases')
        col_names = ['StringencyIndex'] + col_names_f
        cur_tr = translation_dict['Response_Oxford']
        cur_df.rename(columns=cur_tr, inplace=True)

        cur_df.sort_values(by=['CountryName', 'date'],inplace=True)
        cur_df.reset_index(inplace=True)
        text_col = []
        for index in cur_df.index:
            cur_str = []
            if index > 0:
                if cur_df.loc[index - 1, 'CountryName'] == cur_df.loc[index, 'CountryName']:
                    for col_i,cur_col in enumerate(col_names_f):
                        if not(np.isnan(cur_df.loc[index,cur_col]) and np.isnan(cur_df.loc[index-1,cur_col])) and \
                                cur_df.loc[index,cur_col] != cur_df.loc[index-1,cur_col]:
                            if col_i%2==0:
                                new_str = '{}:{}→{}'.format(cur_col,cur_df.loc[index-1,cur_col],cur_df.loc[index,cur_col])
                            else:
                                new_str = 'Flag of {}:{}→{}'.format(col_names_f[col_i-1], cur_df.loc[index-1, cur_col], cur_df.loc[index, cur_col])
                            cur_str.append(new_str)
            cur_str = "<br>".join(cur_str)
            text_col.append(cur_str)
        cur_df['text'] = text_col

        all_data_dict[fs_key] = {'df':cur_df,'countries':countries,'col_names':col_names}
        filesize_dict[fs_key]['is_new'] = False


    countries = all_data_dict['Response_Oxford']['countries']

    health_flag = False
    for country_in in countries:
        if country_in == 'Italy':
            fs_key = '{}_Nation'.format(country_in)
            fs_key_region = '{}_Region'.format(country_in)
            fs_key_province = '{}_Province'.format(country_in)
            if filesize_dict[fs_key]['is_new'] or not all_data_dict:
                app.server.logger.info('Refreshing {}'.format(fs_key))

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
            health_cols = ['date','CountryName','total_cases','deaths']
            health_opts = health_cols[2:]
            if health_flag == False:
                all_data_dict['health_opts'] = health_opts
                health_flag = True
            df_nation = all_data_dict['Response_Oxford']['df'].loc[:,health_cols]
            data = {'Country': {'data': df_nation, 'options': health_opts, 'norm': health_opts,'cols': [country_in],'loc':'CountryName'}}
            all_data_dict[country_in] = data



def save_data(data_dir,filesize_dict,app,reload_flag=True):
    from constants import urls
    import requests
    import os
    import json
    from urllib.parse import urlparse

    for key1, value1 in urls.items():
        for key2, value2 in value1.items():

            if key2=='Apple':
                #https://towardsdatascience.com/empowering-apple-mobility-trends-reports-with-bigquery-and-data-studio-1b188ab1c612

                loop_flag = True
                ver_num = 0
                while loop_flag:
                    response = requests.head(value2.format('v{}'.format(ver_num+1)), allow_redirects=True)
                    if response.status_code == 200:
                        ver_num += 1
                    else:
                        loop_flag = False

                if ver_num > 0:
                    app.server.logger.info('Apple version: {}'.format(ver_num))
                    r_apple = requests.get(value2.format('v{}'.format(ver_num)))
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
                #reload_flag = (fname not in filesize_dict) or not os.path.exists(file_path)

                filesize_dict[fname] = {'size': size, 'is_new': True, 'f_path': file_path}
                if status_code==200 and reload_flag:
                    app.server.logger.info('Downloading {}'.format(fname))
                    myFile = requests.get(url_name)
                    open(file_path, 'wb').write(myFile.content)



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