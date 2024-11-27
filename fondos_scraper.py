#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FONDOS.gob Scraper
=================

Este script es un web scraper diseñado para extraer información de concursos y fondos
públicos desde el sitio web https://fondos.gob.cl/searchernew/

El scraper recolecta información detallada sobre cada fondo, incluyendo:
- Estado y alcance del fondo
- Institución responsable
- Nombre del fondo
- Beneficiarios
- Fechas de inicio y fin
- Montos asignados
- Descripción detallada
- Categoría
- Enlaces a bases y documentación

Características:
--------------
- Manejo de User-Agents aleatorios para evitar bloqueos
- Guardado incremental de datos en CSV
- Manejo de errores robusto
- Delays aleatorios entre requests para no sobrecargar el servidor

Uso:
----
    $ python fondos_scraper.py

Requisitos:
----------
- Python 3.7+
- requests
- beautifulsoup4
- pandas
- lxml

Author: mlorca
Date: 2023
License: MIT
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

def get_user_agent() -> str:
    """
    Retorna un User-Agent aleatorio para simular diferentes navegadores.
    
    Esta función ayuda a evitar bloqueos por parte del servidor al variar
    el User-Agent en cada petición.

    Returns:
        str: String con un User-Agent aleatorio de una lista predefinida
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
    ]
    return random.choice(user_agents)

def get_detail_info(url: str) -> dict:
    """
    Obtiene información detallada de la página específica del fondo.
    
    Esta función accede a la página individual de cada fondo para extraer
    información adicional que no está disponible en la lista principal.
    
    Args:
        url (str): URL completa de la página del fondo

    Returns:
        dict: Diccionario con la siguiente información:
            - DESCRIPCION (str): Descripción completa del fondo
            - CATEGORIA (str): Categoría del fondo
            - WEB (str): URL de las bases del concurso

    Raises:
        requests.RequestException: Si hay problemas al acceder a la URL
        ValueError: Si el parseo del HTML falla
    """
    try:
        headers = {
            'User-Agent': get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extraer descripción y categoría
        descripcion = ""
        categoria = ""
        web_bases = ""
        
        # Descripción está en el primer <p> después del h1
        descripcion_div = soup.find('div', class_='mb-4 d-block')
        if descripcion_div:
            descripcion_p = descripcion_div.find('p')
            if descripcion_p:
                descripcion = descripcion_p.text.strip()
        
        # Categoría está en un span dentro de un div con clase me-3
        categoria_divs = soup.find_all('div', class_='me-3')
        for div in categoria_divs:
            small = div.find('small')
            if small and 'Categoría:' in small.text:
                categoria_span = div.find('span', class_='bg-rosa')
                if categoria_span:
                    categoria = categoria_span.text.strip()
                break
        
        # Buscar el enlace en el contenido de las bases
        bases_div = soup.find('div', id='pills-04')
        if bases_div:
            enlaces = bases_div.find_all('a')
            if enlaces:
                web_bases = enlaces[0].get('href', '')
        
        return {
            "DESCRIPCION": descripcion,
            "CATEGORIA": categoria,
            "WEB": web_bases
        }
        
    except requests.RequestException as e:
        print(f"Error obteniendo detalles de {url}: {str(e)}")
        raise
    except ValueError as e:
        print(f"Error parseando HTML de {url}: {str(e)}")
        raise

def extract_fondo_info(card: BeautifulSoup) -> dict:
    """
    Extrae la información de un fondo desde su card HTML.
    
    Procesa el HTML de una tarjeta individual de fondo para extraer
    todos los campos relevantes.
    
    Args:
        card (BeautifulSoup): Elemento HTML que contiene la información del fondo

    Returns:
        dict: Diccionario con la siguiente información:
            - URL (str): URL completa del fondo
            - ESTADO (str): Estado actual del fondo
            - ALCANCE (str): Alcance territorial
            - INSTITUCIÓN (str): Nombre de la institución
            - NOMBRE (str): Nombre del fondo
            - BENEFICIARIO (str): Tipo de beneficiarios
            - INICIO (str): Fecha de inicio
            - FIN (str): Fecha de término
            - MONTO (str): Monto del fondo
            - FECHA_EXTRACCION (str): Timestamp de la extracción

    Raises:
        ValueError: Si no se puede extraer la información requerida
    """
    try:
        # URL
        url_element = card.find('a')
        url = url_element['href'] if url_element else ''
        if not url.startswith('http'):
            url = 'https://fondos.gob.cl' + url
            
        # Estado y Alcance
        estado_element = card.find('span', class_='badge')
        estado = estado_element.text.strip() if estado_element else ''
        
        alcance_element = card.find('span', class_='text-white') or card.find('span', class_='text-dark')
        alcance = alcance_element.text.strip() if alcance_element else ''
        alcance = alcance.replace('', '').strip()  # Eliminar ícono
        
        # Institución y Nombre
        institucion_element = card.find('small', class_='text-uppercase')
        institucion = institucion_element.text.strip() if institucion_element else ''
        
        nombre_element = card.find('h6')
        nombre = nombre_element.text.strip() if nombre_element else ''
        
        # Beneficiarios, Fechas y Montos
        card_body = card.find('div', class_='card-body')
        if card_body:
            paragraphs = card_body.find_all('p')
            beneficiario = paragraphs[0].text.strip() if len(paragraphs) > 0 else ''
            
            fechas = paragraphs[1].text.strip() if len(paragraphs) > 1 else ''
            inicio = ''
            fin = ''
            if 'Inicio:' in fechas and 'Fin:' in fechas:
                fechas_split = fechas.split('|')
                inicio = fechas_split[0].replace('Inicio:', '').strip()
                fin = fechas_split[1].replace('Fin:', '').strip()
            
            monto = paragraphs[2].text.strip() if len(paragraphs) > 2 else ''
        else:
            beneficiario = ''
            inicio = ''
            fin = ''
            monto = ''
        
        return {
            'URL': url,
            'ESTADO': estado,
            'ALCANCE': alcance,
            'INSTITUCIÓN': institucion,
            'NOMBRE': nombre,
            'BENEFICIARIO': beneficiario,
            'INICIO': inicio,
            'FIN': fin,
            'MONTO': monto,
            'FECHA_EXTRACCION': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except ValueError as e:
        print(f"Error extrayendo información de fondo: {str(e)}")
        raise

def save_fondo_to_csv(fondo: dict, index: int, file_exists: bool = False) -> None:
    """
    Guarda un fondo individual en el archivo CSV.
    
    Permite guardar de forma incremental la información de cada fondo,
    manteniendo un ID único para cada registro.
    
    Args:
        fondo (dict): Diccionario con la información del fondo
        index (int): Índice para el ID del fondo
        file_exists (bool, optional): Indica si el archivo ya existe. Defaults to False.

    Raises:
        IOError: Si hay problemas escribiendo el archivo
        ValueError: Si los datos del fondo son inválidos
    """
    try:
        # Crear DataFrame con un solo fondo
        df = pd.DataFrame([fondo])
        
        # Agregar ID
        df.insert(0, 'ID', [index])
        
        # Guardar a CSV
        mode = 'a' if file_exists else 'w'
        header = not file_exists
        df.to_csv('fondos.csv', mode=mode, header=header, index=False)
        print(f"Fondo {index} guardado: {fondo['NOMBRE']}")
        
    except IOError as e:
        print(f"Error escribiendo archivo CSV: {str(e)}")
        raise
    except ValueError as e:
        print(f"Error en los datos del fondo: {str(e)}")
        raise

def get_fondos() -> int:
    """
    Obtiene la información de todos los fondos disponibles.
    
    Realiza el scraping principal del sitio, procesando cada fondo
    encontrado y guardándolo en el archivo CSV.
    
    Returns:
        int: Número total de fondos procesados exitosamente

    Raises:
        requests.RequestException: Si hay problemas accediendo al sitio
        ValueError: Si hay problemas procesando la información
    """
    url = 'https://fondos.gob.cl/searchernew/'
    headers = {
        'User-Agent': get_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Encontrar todas las cards de fondos
        cards = soup.find_all('div', class_='col-md-6 col-lg-3')
        
        count = 0
        for card in cards:
            fondo_info = extract_fondo_info(card)
            if fondo_info:
                # Obtener información detallada de la página del fondo
                detail_info = get_detail_info(fondo_info['URL'])
                fondo_info.update(detail_info)
                
                # Guardar el fondo en el CSV
                count += 1
                save_fondo_to_csv(fondo_info, count, count > 1)
                
                time.sleep(random.uniform(1, 3))  # Espera aleatoria entre requests
        
        return count
        
    except requests.RequestException as e:
        print(f"Error accediendo al sitio: {str(e)}")
        raise
    except ValueError as e:
        print(f"Error procesando la información: {str(e)}")
        raise

def main():
    """
    Función principal del script.
    
    Inicializa el proceso de scraping y maneja los errores principales.
    Imprime estadísticas básicas al finalizar el proceso.
    """
    print("Iniciando extracción de fondos desde fondos.gob.cl...")
    try:
        total_fondos = get_fondos()
        print(f"\nProceso completado exitosamente!")
        print(f"Total de fondos procesados: {total_fondos}")
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")
        raise

if __name__ == "__main__":
    main()
