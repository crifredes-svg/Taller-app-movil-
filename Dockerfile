# Imagen base ligera
FROM nginx:alpine

# Exponer el puerto 80 del contenedor
EXPOSE 80

# Comando de inicio
CMD ["nginx", "-g", "daemon off;"]