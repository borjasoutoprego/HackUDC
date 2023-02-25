# HackUDC

**Año 2023**

Proyecto desarrollado en el hackatón *HackUDC* como solución al reto propuesto por la empresa patrocinadora *Gradiant*. 

Consiste en un `Sistema de recomendación de arenales` según `preferencias de actividad` y `predicción meteorológica`

Se implementan diferentes capas de funcionalidad: 
  
  * Recomendación para 1 persona
  * Recomendación para un grupo de personas
  * Recomendación para día y hora concretos
  * Recomendación considerando la distancia máxima especificada por el usuario
  
Para el desarrollo del proyecto se utiliza una base de datos con información de las playas obtenida en: https://opendata.esri.es/datasets/ComunidadSIG::playas-espa%C3%B1olas/about .

Además, se amplía la información a través de las siguientes APIs: http://api.weatherapi.com/ y https://marine-api.open-meteo.com/, de donde se obtienen datos meteorológicos y marítimos de las diferentes playas, respectivamente.
