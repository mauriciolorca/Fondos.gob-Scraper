# FONDOS.gob Scraper

Este script extrae información detallada de los concursos y fondos disponibles en el sitio web [FONDOS.gob](https://fondos.gob.cl/searchernew/). La información se guarda incrementalmente en un archivo CSV, permitiendo monitorear el progreso de la extracción.

## Características

- Extracción completa de información de fondos gubernamentales
- Guardado incremental en CSV (fondo por fondo)
- Manejo de errores robusto
- Rotación de User-Agents para evitar bloqueos
- Documentación detallada del código
- Mensajes de progreso en tiempo real

## Información Extraída

Para cada fondo, se extrae:

- ID (generado automáticamente)
- URL del fondo
- Estado (abierto/cerrado)
- Alcance territorial
- Institución responsable
- Nombre del fondo
- Beneficiarios
- Fecha de inicio
- Fecha de término
- Monto
- Descripción detallada
- Categoría
- URL de las bases
- Fecha y hora de extracción

## Estructura del Proyecto

```
FONDOS.gob-Scraper/
├── fondos_scraper.py     # Script principal
├── requirements.txt      # Dependencias
├── README.md            # Documentación
├── LICENSE             # Licencia MIT
├── .gitignore         # Configuración de Git
└── fondos.csv         # Archivo de salida (generado)
```

## Requisitos

```
beautifulsoup4==4.12.2
pandas==2.1.1
requests==2.31.0
lxml==4.9.3
```

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/FONDOS.gob-Scraper.git
cd FONDOS.gob-Scraper
```

2. Crear y activar un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecutar el script principal:
```bash
python fondos_scraper.py
```

El script mostrará el progreso de la extracción y guardará los resultados en `fondos.csv`. Cada fondo se guarda inmediatamente después de ser procesado, lo que permite:
- Monitorear el progreso en tiempo real
- Verificar la calidad de los datos extraídos
- No perder el progreso si el script se interrumpe

## Notas Técnicas

- El script utiliza requests y BeautifulSoup4 para el scraping
- Se implementa rotación de User-Agents para evitar bloqueos
- Los errores son manejados y registrados apropiadamente
- La información se extrae de manera respetuosa con el servidor (delays entre requests)
- El guardado incremental permite procesar grandes cantidades de fondos de manera segura

## Manejo de Errores

El script incluye manejo de errores para:
- Problemas de conexión
- Páginas no encontradas
- Elementos faltantes en el HTML
- Errores de escritura en el CSV

Los errores se registran en la consola con mensajes descriptivos.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un Fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Tu Nombre - [@tu_twitter](https://twitter.com/tu_twitter)

Project Link: [https://github.com/tu-usuario/FONDOS.gob-Scraper](https://github.com/tu-usuario/FONDOS.gob-Scraper)
