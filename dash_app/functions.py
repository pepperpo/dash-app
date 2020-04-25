import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import time

def generate_plot(dash_session,aggr_in,col_in,norm_in,log_in,region_in,prov_in):

    fig = go.Figure()
    fig.update_layout( margin={'t': 0})

    options = dash_session['options_nation']
    if not col_in:
        col_in = options

    fig_data = []
    annot_flag = [False]

    t1 = time.time()

    if not region_in and not prov_in:
        df = pd.DataFrame(dash_session['nation'])
        plot_df(df, fig_data,annot_flag,aggr_in,col_in,norm_in,log_in)

    if region_in:
        for cur_region in region_in:
            if cur_region == '{}'.format(dash_session['nation_str']):
                df = pd.DataFrame(dash_session['nation'])
            else:
                df = pd.DataFrame(dash_session['region'])
                cur_idx = df['denominazione_regione']==cur_region
                df = df.loc[cur_idx]
            plot_df(df, fig_data,annot_flag,aggr_in,col_in,norm_in,log_in,suffix='({})'.format(cur_region))

    if prov_in:
        for cur_prov in prov_in:
            df = pd.DataFrame(dash_session['province'])
            cur_idx = df['denominazione_provincia'] == cur_prov
            df = df.loc[cur_idx]
            cur_col = [value for value in col_in if value in dash_session['options_province']]
            plot_df(df, fig_data, annot_flag, aggr_in, cur_col, norm_in, log_in, suffix='({})'.format(cur_prov))

    #print('Time elapsed {}'.format(time.time()-t1))

    if annot_flag[0] is True:
        annotations = [
            dict(
                x=0.5,
                y=0.1,
                showarrow=False,
                text="Some variables were deleted because log of a negative value",
                xref="paper",
                yref="paper"
            )]
    else:
        annotations = []

    fig = go.Figure(data=fig_data)

    # Change the bar mode
    #fig.update_layout(barmode='relative',hovermode='x unified')
    fig.update_layout(hovermode='x unified',yaxis_type=log_in,annotations=annotations,margin={'t': 0})

    return fig


def plot_df(df,fig_data,annot_flag,aggr_in,col_in,norm_in,log_in,suffix=''):
    date = pd.to_datetime(df['data'])

    if norm_in:
        if aggr_in == 'tot':
            denom = df[norm_in]
        else:
            denom = df[norm_in].diff()  # np.concatenate([[1], df[norm_in].diff()])
    else:
        denom = 1.


    for cur_col in col_in:
        if aggr_in == 'tot':
            numer = df[cur_col]
        else:
            numer = df[cur_col].diff()  # np.concatenate([[0],df[cur_col].diff()])

        # fig_data.append(go.Bar(name=cur_col, x=date, y=numer/denom))

        y_val = numer / denom

        if not (np.any(y_val < 0) and log_in == 'log'):
            fig_data.append(go.Scatter(name='{}{}'.format(cur_col,suffix), x=date, y=y_val, mode='lines+markers'))
        else:
            annot_flag[0] = True



def load_data(repo_in,all_data_dict,filesize_dict):

    from constants import translation_dict

    if repo_in == 'Italy':
        fs_key = '{}_Nation'.format(repo_in)
        fs_key_region = '{}_Region'.format(repo_in)
        fs_key_province = '{}_Province'.format(repo_in)

        if filesize_dict[fs_key]['is_new'] or not all_data_dict:

            cur_tr = translation_dict[repo_in]

            df_nation = pd.read_csv(
                filesize_dict[fs_key]['f_path'],
                header=0)
            df_region = pd.read_csv(
                filesize_dict[fs_key_region]['f_path'],
                header=0)
            df_province = pd.read_csv(
                filesize_dict[fs_key_province]['f_path'],
                header=0)

            options_nation_region_it = ['ricoverati_con_sintomi','terapia_intensiva','totale_ospedalizzati','isolamento_domiciliare','totale_positivi','dimessi_guariti','deceduti','totale_casi','tamponi','casi_testati']
            options_province_it = ['totale_casi']

            #apply translations
            options_nation_region = [cur_tr[cur_var] for cur_var in options_nation_region_it]
            options_province = [cur_tr[cur_var] for cur_var in options_province_it]
            df_nation.rename(columns=cur_tr, inplace=True)
            df_region.rename(columns=cur_tr, inplace=True)
            df_province.rename(columns=cur_tr, inplace=True)

            data = {'nation':df_nation,
                    'options_nation':options_nation_region,
                    'region': df_region,
                    'options_region': options_nation_region,
                    'province': df_province,
                    'options_province': options_province,
                    'nation_str': repo_in
                    }

            all_data_dict[repo_in] = data
            filesize_dict[fs_key]['is_new'] = False

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

                reload_flag = (fname not in filesize_dict) or size > filesize_dict[fname]['size'] or not os.path.exists(file_path)

                if status_code==200 and reload_flag:
                    myFile = requests.get(url_name)
                    open(file_path, 'wb').write(myFile.content)
                    filesize_dict[fname]={'size':size,'is_new':True,'f_path':file_path}


def data2dropdown(country_in,dict_in):
    region_list = []
    province_list = []
    cur_dict = dict_in[country_in]
    if country_in=='Italy':
        region_list = [country_in] + sorted(cur_dict['region']['denominazione_regione'].unique().tolist())
        province_list = sorted(cur_dict['province']['denominazione_provincia'].unique().tolist())
        province_list.remove('In fase di definizione/aggiornamento')

        region_drp = []
        for cur_i,cur_opt in enumerate(region_list):
            if cur_i==0:
                cur_label = cur_opt + ' [aggregate]'
            else:
                cur_label = cur_opt
            region_drp.append({'label': cur_label, 'value': cur_opt})

        #region_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in region_list]
        province_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in province_list]

    return region_drp, province_drp


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