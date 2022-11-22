import requests
import re
import pandas as pd
import numpy as np
from pprint import pprint
from PyInquirer import prompt
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = 'https://www.ine.es'
REGION_URL = '/dynt3/inebase/index.htm?padre=7132'
DIMENSION_URL = '/dynt3/inebase/ajax/es/listaCapitulos.htm'
POST_URL = 'jaxiT3/Datos.htm'


def main():
    regions = get_region_options()
    # pprint(regions)

    url_dim, id_dim = get_dimension_options(regions)

    # pprint(url_dim)
    id_dim = id_dim.split('_')[1]

    param_page = get_param_page(url_dim)

    territories = get_territories_options()
    territories_ids = get_territories_ids(param_page)

    criteria = get_criteria_id(param_page)

    period = get_time_options(param_page)

    form_dict = create_form_data(territories, territories_ids, criteria, period)

    req_post = create_post_req(form_dict, id_dim)

    try:
        create_statistics_csv(req_post)
    except:
        print("Error generar la petición de generación de csv")
        print(f"url: {req_post.request.url}")
        print(f"data: {req_post.request.body}")


def get_region_options():
    """
    Recupera las comunidades autónomas y sus id para buscar las dimensiones asociadas.
    :return: id region
    """

    # Get HTML content
    req = requests.get(urljoin(BASE_URL, REGION_URL))
    soup = BeautifulSoup(req.text, 'html.parser')
    soup_ls_poblaciones = soup.find('ul', class_="secciones").findChildren("li")

    # Extraemos la tupla de nombre de la comunidad autónoma y el identificador del enlace para navegar posteriormente.
    ls_poblacion_id = [(ac_name.find('a').get_text().strip(), ac_name.find('a').attrs.get('id'))
                       for ac_name in soup_ls_poblaciones]

    choice_list = list()

    for a, b in ls_poblacion_id:
        choice_dict = dict()
        choice_dict['key'] = b
        choice_dict['name'] = a
        choice_dict['value'] = b
        choice_list.append(choice_dict)

    regions_prompt = {
        'type': 'list',
        'name': 'region',
        'message': 'Selecciona una comunidad autónoma:',
        'choices': choice_list
    }

    answers = prompt(regions_prompt)

    return answers['region']


def get_dimension_options(answer: str):
    answer_clean = answer.split("_")[1]

    params = {
        "padre": answer_clean,
        "idp": "."
    }

    # Pasamos el identificador de la lista previa
    req = requests.get(urljoin(BASE_URL, DIMENSION_URL), params=params)
    # Get HTML content
    soup = BeautifulSoup(req.text, 'html.parser')
    # Recuperamos los nuevos enlaces y los idetificadores
    a_tipo_consulta_list = soup.find_all('a', class_="titulo t4")
    # Creamos con Nombre y url de las opciones
    # Filtramos las dimension que tienen filtros por edad, sexo, etc
    ls_dimension_id = list()
    for ac_name in a_tipo_consulta_list:
        if not re.search("Porcentaje de población", ac_name.get_text().strip()):
            ls_dimension_id.append((ac_name.get_text().strip(), ac_name.attrs.get('href'), ac_name.attrs.get('id')))

    choice_list = list()

    # Poblamos las opciones
    for a, b, c in ls_dimension_id:
        choice_dict = dict()
        choice_dict['key'] = b
        choice_dict['name'] = a
        choice_dict['value'] = (b, c)
        choice_list.append(choice_dict)

    dimension_prompt = {
        'type': 'list',
        'name': 'dimension',
        'message': 'Selecciona la dimension a consultar:',
        'choices': choice_list
    }

    answers = prompt(dimension_prompt)

    return answers['dimension']


def get_param_page(url: str):
    complete_url = urljoin(BASE_URL, url)
    req = requests.get(complete_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    param_page = soup.find_all('ul', class_='variables')[0]

    return param_page


def get_territories_options():
    choice_list = list()
    literal_list = ['Municipios', 'Distritos', 'Secciones']
    # Poblamos las opciones
    for i in range(0, 3):
        choice_dict = dict()
        choice_dict['key'] = f"selCri_{i}"
        choice_dict['name'] = literal_list[i]
        choice_dict['value'] = f"selCri_{i}"
        choice_list.append(choice_dict)

    territories_prompt = {
        'type': 'checkbox',
        'name': 'territory',
        'message': 'Selecciona la tipología de territorio:',
        'choices': choice_list
    }

    answers = prompt(territories_prompt)

    return answers['territory']


def get_territories_ids(soup):
    # Recupero el identificador para la consulta de territorios
    tr = soup.find_all_next('li', {'id': re.compile(r'^tg')})[0]
    id_tr = tr.attrs['id']
    id_tr = id_tr[2:]

    # Recupero el identificador para cada territorio
    filter_tr = soup.find_all('script')[0].contents[0]
    list_ids_tr = re.findall(r"\[([A-Za-z0-9\,]+)\]", filter_tr)[0].split(",")

    # Instanciamos el objeto a devolver
    tr_object = dict()
    tr_object['id'] = id_tr
    tr_object['values'] = list_ids_tr

    return tr_object


def get_criteria_options(soup):
    # Recuperamos las lista de criterios de búsqueda
    cr = soup.find_all_next('li', {'id': re.compile(r'^tg')})[1]
    list_cr = cr.find_all('option', class_="jP_0")
    list_id_tr = [(tag.contents[0], tag.attrs.get('value')) for tag in list_cr]

    choice_list = list()

    # Poblamos las opciones
    for a, b in list_id_tr:
        choice_dict = dict()
        choice_dict['key'] = b
        choice_dict['name'] = a
        choice_dict['value'] = b
        choice_list.append(choice_dict)

    criteria_prompt = {
        'type': 'list',
        'name': 'criteria',
        'message': 'Selecciona el criterio a consultar:',
        'choices': choice_list
    }

    answers = prompt(criteria_prompt)

    return answers['criteria']


def get_criteria_id(soup):
    # Recupero la categoria de busqueda
    cr = soup.find_all_next('li', {'id': re.compile(r'^tg')})[1]
    id_cr = cr.attrs['id']
    id_cr = id_cr[2:]

    # Pregunta el criterio a consultar
    criteria = get_criteria_options(soup)

    cri_dict = dict()
    cri_dict['id'] = id_cr
    cri_dict['value'] = criteria
    # pprint(cri_dict)

    return cri_dict


def get_time_options(soup):
    # Recupero la categoría de tiempo
    pr = soup.find_all('select', id='periodo')[0]

    list_pr = pr.findAll('option')
    list_id_pr = [(tag.contents[0], tag.attrs.get('value')) for tag in list_pr]

    choice_list = list()

    # Poblamos las opciones
    for a, b in list_id_pr:
        choice_dict = dict()
        choice_dict['key'] = b
        choice_dict['name'] = a
        choice_dict['value'] = b
        choice_list.append(choice_dict)

    period_prompt = {
        'type': 'list',
        'name': 'period',
        'message': 'Selecciona el año a consultar:',
        'choices': choice_list
    }

    answers = prompt(period_prompt)

    return answers['period']


def create_form_data(pob_type: list, pob_ids: dict, crit: dict, period):
    """
    Función que crea el dict con la información del formulario con la petición para la generación de la petición POST para la web del INE.

    :param pob_type: Tipo de población (Municipio,Distrito,Sección).
    :param pob_ids: Dict con Id de la comunidad autónoma y lista de ids de las poblaciones.
    :param crit: Id de criterio de búsqueda.
    :param period: Id de periodo de búsqueda.
    :return: Formulario
    """

    # Inicializamos dict con parámetros por defecto
    form_dict = dict()

    form_dict['isPx'] = 'false'
    form_dict['L'] = '0'
    form_dict['fromTabla'] = '1'
    form_dict['formatoVisible'] = '1'
    form_dict['oper'] = '353'
    form_dict['sel_oper'] = '1'

    # Añadimos los parámetros variables
    pob_id = pob_ids['id']
    busc_pob = f'busc_{pob_id}'
    form_dict[busc_pob] = ''

    # Tipos población
    for tp in pob_type:
        form_dict[tp] = 'on'

    # Ids de población
    cri_pob = f'cri{pob_id}'
    form_dict[cri_pob] = pob_ids['values']

    # Criterio
    cri_id = crit['id']
    busc_cri = f'busc_{cri_id}'
    orden_cri = f'orden_{cri_id}'
    form_dict[busc_cri] = ''
    form_dict[orden_cri] = ''

    cri_cri = f'cri{cri_id}'
    form_dict[cri_cri] = crit['value']

    # Población
    form_dict['busc_periodo'] = ''
    form_dict['orden_periodo'] = 'DESC'
    form_dict['periodo'] = period

    # Resto variables
    form_dict['columns'] = [cri_id, 'p_per']
    form_dict['rows'] = pob_id
    form_dict['formato_tabla_dec'] = ''
    form_dict['totalOps'] = '4'
    form_dict['numCri'] = '-1'

    return form_dict


def create_post_req(fd: dict, id_t: str):
    """

    :param fd: Formulario a enviar en la peticion post.
    :param id_t: Identificador de la tabla de la petición post.
    :return:
    """
    # Genermos la peticion post
    params = {"t": id_t}
    url = urljoin(BASE_URL, POST_URL)
    req = requests.post(url, data=fd, params=params)

    return req


def create_statistics_csv(req):
    """
    Genera un csv con las estadísticas recuperadas de la web del INE en base a los parámetros seleccionados por el usuario.

    :param req: Peticion post.
    :return:
    """

    soup = BeautifulSoup(req.text, features='lxml')

    def get_pob_name(arr):
        """
        Función interna para recuperar el nombre de la población.

        :param arr:
        :return:
        """
        arr_tmp = list()

        for val in arr:
            if not val.isnumeric():
                arr_tmp.append(val)

        arr_final = arr_tmp[0:len(arr_tmp) - 1]
        pob_name = ' '.join(map(str, arr_final))

        return pob_name

    def get_pob_ids(df: pd.DataFrame):
        """
        Función para crear las columnas de municipio, distrito y sección dentro del dataframe.

        :param df:
        :return:
        """

        id_mix_lst = df.poblacion_mix.split(' ')
        id_mix = id_mix_lst[0]
        len_id = len(id_mix)

        id_distrito = np.nan
        id_seccion = np.nan

        if len_id == 5:
            id_poblacion = id_mix
            nom_poblacion = id_mix_lst[1]
        elif len_id == 7:
            id_poblacion = id_mix[0:5]
            id_distrito = id_mix[5:7]
            nom_poblacion = get_pob_name(id_mix_lst)
        else:
            id_poblacion = id_mix[0:5]
            id_distrito = id_mix[5:7]
            id_seccion = id_mix[7:10]
            nom_poblacion = get_pob_name(id_mix_lst)

        return pd.Series({'id_poblacion': id_poblacion, 'id_distrito': id_distrito, 'id_seccion': id_seccion,
                          'nom_poblacion': nom_poblacion})

    crit = str(soup.find('th', id="c_A0").contents[0])
    year = str(soup.find('th', id="c_B0").contents[0])

    col_pob = [tag.text for tag in soup.find('tbody').findChildren('th')]
    col_val = [tag.text for tag in soup.find('tbody').findChildren('td')]

    df_ine = pd.DataFrame(list(zip(col_pob, col_val)),
                          columns=['poblacion_mix', 'metrica'])

    # Añadimos las colummas estáticas
    df_ine['dimension'] = crit
    df_ine['año'] = year

    # Descompactamos las variables relativas a la población
    df_ine[['id_poblacion', 'id_distrito', 'id_seccion', 'nom_poblacion']] = df_ine[['poblacion_mix']].apply(
        get_pob_ids, axis=1)

    df_ine.drop(columns=['poblacion_mix'], inplace=True)

    df_ine = df_ine[['id_poblacion', 'id_distrito', 'id_seccion', 'nom_poblacion', 'metrica', 'dimension', 'año']]

    # Nombre a asignar al csv
    dt = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f"estadisticas_ine_{dt}.csv"

    df_ine.to_csv(name, index=False)

    print(f"CSV con nombre {name} generado correctamente.")


if __name__ == "__main__":
    print("Atlas de distribución de renta de los hogares")
    main()
