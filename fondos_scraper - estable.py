#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FONDOS.gob Scraper

Este script extrae información de los concursos publicados en el sitio web
https://fondos.gob.cl/searchernew/

Author: mlorca
Date: 2023
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

def get_user_agent():
    """Retorna un User-Agent aleatorio para simular diferentes navegadores."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
    ]
    return random.choice(user_agents)

def extract_fondo_info(card):
    """
    Extrae la información de un fondo desde su card HTML.
    
    Args:
        card (BeautifulSoup): Elemento HTML que contiene la información del fondo
        
    Returns:
        dict: Diccionario con la información extraída
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
        
    except Exception as e:
        print(f"Error extrayendo información de fondo: {str(e)}")
        return None

def get_fondos():
    """
    Obtiene la información de todos los fondos disponibles.
    
    Returns:
        list: Lista de diccionarios con la información de cada fondo
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
        
        fondos = []
        for card in cards:
            fondo_info = extract_fondo_info(card)
            if fondo_info:
                fondos.append(fondo_info)
        
        return fondos
        
    except Exception as e:
        print(f"Error obteniendo fondos: {str(e)}")
        return []

def save_to_csv(fondos):
    """
    Guarda la información de los fondos en un archivo CSV.
    
    Args:
        fondos (list): Lista de diccionarios con la información de los fondos
    """
    if not fondos:
        print("No hay fondos para guardar")
        return
        
    try:
        # Crear DataFrame
        df = pd.DataFrame(fondos)
        
        # Agregar ID
        df.insert(0, 'ID', range(1, len(df) + 1))
        
        # Guardar a CSV
        df.to_csv('fondos.csv', index=False)
        print(f"Se guardaron {len(df)} fondos en fondos.csv")
        
    except Exception as e:
        print(f"Error guardando CSV: {str(e)}")

def main():
    """Función principal del script."""
    print("Iniciando extracción de fondos...")
    fondos = get_fondos()
    
    if fondos:
        print(f"\nSe encontraron {len(fondos)} fondos")
        save_to_csv(fondos)
    else:
        print("No se encontraron fondos")

if __name__ == "__main__":
    main()
