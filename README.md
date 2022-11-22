# PRA 1 - Web Scrapping
## Autor: Carlos José Ospina
## Configuración

Para el correcto funcionamiento del script, es necesario instalar las dependencias mediante el comando.

```
 pip install -r requirements.txt
```

Este scrip tiene como objetivo obtener del INE los datos demográficos y de renta de una determinada comunidad autónoma de forma simple e interactiva.

## Ejecución del script

```
 python3 scrap_spanish_demografics.py
```


## Detalle funcional

La herramienta CLI es capaz de generar a demanda un dataset en formato **csv** que tiene la siguiente estructura:

| **Nombre**           | **Descripción**                       |
|----------------------|---------------------------------------|
| **id_poblacion**     | Identificador de la población         |
| **id_distrito**      | Identificador del distrito            |
| **id_seccion**       | Identificador de la sección censal    |
| **nombre_poblacion** | Nombre de la población                |
| **metrica**          | Valor de la métrica                   |
| **dimension**        | Descripción de la dimension obtenida: |
| **año**              | Fecha referencia de datos             |

 

* Indicadores de renta media y mediana
  * Renta neta media por persona
  * Renta neta media por hogar
  * Media de la renta por unidad de consumo
  * Mediana de la renta por unidad de consumo
  * Renta bruta media por persona
  * Renta bruta media por hogar 
* Distribución por fuente de ingresos
  * Renta bruta media por persona
  * Fuente de ingreso: salario
  * Fuente de ingreso: pensiones
  * Fuente de ingreso: prestaciones por desempleo
  * Fuente de ingreso: otras prestaciones
  * Fuente de ingreso: otros ingresos
* Índice de Gini y Distribución de la renta P80/P20
  * Indice Gini
  * Distribución de la renta P80/P20
* Indicadores demográficos
  * Edad media de la población
  * Porcentaje de la población menor de 18 años
  * Porcentaje de la población de 65 o más años
  * Tamaño medio del hogar
  * Porcentaje de hogares unipersonales
  * Población
  * Porcentaje de población España


## Licencia

Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg