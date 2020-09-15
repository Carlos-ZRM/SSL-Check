# Instalación 
## Construir la imagen 
```
docker build -t ssl-check .
``` 

## Montar volumen 
Se debe montar un nuevo volumen y verificar el directorio de montura
```
docker volume create ssl-mount
docker volume inspect ssl-mount | grep Mountpoint
```
## Crear el contenedor

```
docker container run -d --name ssl-check \
    --restart always \
    -v ssl-mount:/app/csv \
    -p 2020:5000 \
    ssl-check
```

## Agregar dominios. 

El contenedor se crea con un archivo nombrado **domains.csv** ahi se agregaran los dominios sin el protocolo. por ejemplo *google.com*

# Uso

## Obtener lista de dominios
- En el navegador **localhost:5000/protocols**
- En la consola :
    ```
    curl -i -H "Content-Type: application/json" -X GET  localhost:5000/protocols
     ``` 

## Obtener reporte de los certificados de servidores
- En el navegador **localhost:5000/hosts**
- En la consola 
    ```
    curl -i -H "Content-Type: application/json" -X GET  localhost:5000/hosts 
    ```
- Descargar archivo 
    ```
    curl -i -H "Content-Type: text/plain" -X GET -o hosts.txt localhost:5000/hosts_txt 
    ```
## Obtener certificados por madurar 
- En el navegador **localhost:5000/certificates** 
- En la consola 
    ```
    curl -i -H "Content-Type: application/json" -X GET  localhost:5000/certificates
    ``` 