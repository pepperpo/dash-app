def save_data(data_dir,filesize_dict,app,reload_flag=True):


    urls = {'Italy': {
        'Nation': 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv',
        'Region': 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv',
        'Province': 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv'},
            'Mobility': {'Apple': 'https://covid19-static.cdn-apple.com/covid19-mobility-data/current/{}/index.json',
                         'Google': 'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'},
            'Response': {'Oxford': 'https://github.com/OxCGRT/covid-policy-tracker/raw/master/data/OxCGRT_latest.csv'}
            }


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
                app.server.logger.info('Size head: {}'.format(size))

                #print(key2,status_code,size)
                url_path = urlparse(url_name).path
                extension = os.path.splitext(url_path)[1]
                file_path = os.path.join(data_dir, fname + extension)

                #reload_flag = (fname not in filesize_dict) or size > filesize_dict[fname]['size'] or not os.path.exists(file_path)
                #reload_flag = (fname not in filesize_dict) or not os.path.exists(file_path)

                filesize_dict[fname] = {'size': size, 'is_new': True, 'f_path': file_path}
                if status_code==200 and reload_flag:
                    app.server.logger.info('Downloading {}'.format(fname))
                    app.server.logger.info(url_name)

                    urllib.request.urlretrieve(url_name, file_path)

                    #myFile = requests.get(url_name)#,headers={'Cache-Control': 'no-cache'})
                    #app.server.logger.info('Size: {}'.format(len(myFile.content)))
                    #open(file_path, 'wb').write(myFile.content)

                    # response = requests.get(url_name, stream=True)
                    # handle = open(file_path, "wb")
                    # for chunk in response.iter_content(chunk_size=512):
                    #     if chunk:  # filter out keep-alive new chunks
                    #         handle.write(chunk)




if __name__ == '__main__':
    app.run_server(debug=debug_flag)