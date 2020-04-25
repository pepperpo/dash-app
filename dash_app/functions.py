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
            if cur_region == '{}[all regions]'.format(dash_session['nation_str']):
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



def load_data(country_in,all_data_dict,app):

    from constants import translation_dict,urls
    import requests

    url_nation = urls[country_in]['Nation']
    response = requests.head(url_nation, allow_redirects=True)
    size = response.headers.get('content-length', 0)

    reload_flag = False
    if all_data_dict:
        prev_size = all_data_dict[country_in]['file_size']
        app.server.logger.info('{}, {}, {}'.format(response.status_code,size,prev_size))
        if response.status_code == 200 and size > prev_size:
            reload_flag = True
        #else:
        #    print("File hasn't changed")

    if not all_data_dict or reload_flag:

        if country_in == 'Italy':
            #print('downloading')

            cur_tr = translation_dict[country_in]

            df_nation = pd.read_csv(
                urls[country_in]['Nation'],
                header=0)
            df_region = pd.read_csv(
                urls[country_in]['Region'],
                header=0)
            df_province = pd.read_csv(
                urls[country_in]['Province'],
                header=0)

            options_nation_region_it = ['ricoverati_con_sintomi','terapia_intensiva','totale_ospedalizzati','isolamento_domiciliare','totale_positivi','dimessi_guariti','deceduti','totale_casi','tamponi','casi_testati']
            options_province_it = ['totale_casi']

            #apply translations
            options_nation_region = [cur_tr[cur_var] for cur_var in options_nation_region_it]
            options_province = [cur_tr[cur_var] for cur_var in options_province_it]
            df_nation.rename(columns=cur_tr,inplace=True)
            df_region.rename(columns=cur_tr,inplace=True)
            df_province.rename(columns=cur_tr,inplace=True)

            data = {'nation':df_nation,
                    'options_nation':options_nation_region,
                    'region': df_region,
                    'options_region': options_nation_region,
                    'province': df_province,
                    'options_province': options_province,
                    'nation_str': country_in,
                    'file_size':size,
                    }

            all_data_dict[country_in] = data




def data2dropdown(country_in,dict_in):
    region_list = []
    province_list = []
    cur_dict = dict_in[country_in]
    if country_in=='Italy':
        region_list = ['{}[all regions]'.format(country_in)] + sorted(cur_dict['region']['denominazione_regione'].unique().tolist())
        province_list = sorted(cur_dict['province']['denominazione_provincia'].unique().tolist())
        province_list.remove('In fase di definizione/aggiornamento')

        region_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in region_list]
        province_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in province_list]

    return region_drp, province_drp



if __name__ == "__main__":
    generate_plot('Italy')