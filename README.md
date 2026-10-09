# Proyecto Taller App Móvil

## Integrantes del Equipo
* **Línea de Desarrollo:** (App Psicosocial)
* **Frontend & UI:** Cristian Flores
* **Backend & DBA:** Diego Anabalon
* **DevOps & Integración:** Cristian Fredes

## Ejecución del backend

La API escucha en el puerto `8000` del contenedor y se publica en el `9000`.
El frontend debe usar `http://<host-del-backend>:9000` o la URL HTTPS entregada
para el API. La base de datos MySQL/MariaDB es un servicio distinto administrado
por 1Panel; su host y puerto no son la URL de la API.

Completa `.env` con el nombre de la base, un usuario MySQL dedicado y su clave.
`DB_HOST` debe ser un host o alias accesible desde el contenedor del backend;
si ambos contenedores no comparten una red Docker, configura una dirección y un
puerto publicados que sean accesibles desde el servidor. No uses la ruta de
archivos de 1Panel como host ni la cuenta `root` para la aplicación.

La aplicación solo admite MySQL/MariaDB y no crea una base local. El contenedor
de MySQL debe compartir la red Docker `1panel-network` con el backend y ser
resoluble como `DB_HOST` (por ejemplo, `mysql`). Configura un usuario dedicado;
no uses las credenciales de root ni los valores por defecto del Compose.

Antes de aplicar migraciones, confirma que la base no tenga tablas o datos que
deban conservarse. En una base nueva, ejecuta `docker compose run --rm backend
alembic upgrade head` y luego `docker compose up --build -d`. La migración más
reciente rellena `codigo_unico` para usuarios que ya existían.

**Seguridad:** todo acceso a datos exige `Authorization: Bearer <token>`.
Registra la cuenta
con `POST /api/v1/usuarios` (incluye contraseña de al menos 12 caracteres) e
inicia sesión con `POST /api/v1/auth/login` para obtener un JWT de 30 minutos.
El registro devuelve el perfil creado y el login devuelve el perfil propio junto
al token para que el cliente pueda cargar la pantalla sin un GET de usuarios.
El JWT se firma con `JWT_SECRET`, que debe ser distinto, aleatorio y de al menos
32 bytes en cada entorno. El registro y login son públicos; los demás endpoints
de datos exigen token. Los recursos por usuario se limitan al propietario, con
excepciones controladas para aceptación de relevos y respuesta a SOS.

En el router de usuarios la única ruta es `POST /api/v1/usuarios` para registro.
No se expone ningún GET para listar o consultar perfiles de usuario.
La pantalla de perfil guarda cambios propios mediante
`PATCH /api/v1/perfil/me`, protegido por bearer; no acepta un ID de usuario.
El texto libre del perfil se guarda en `ocupacion`; `tipo` se mantiene como
clasificación interna `estudiante` o `red`.

Para añadir contactos, el código nuevo se muestra como `RC-` más seis dígitos
hexadecimales (ejemplo `RC-D35C82`). `POST /api/v1/contactos/usuarios/{id}/por-codigo`
acepta ese formato y códigos antiguos de ocho caracteres. Solo requiere código
y relación; apoyos y disponibilidad pueden completarse después. Check-ins
aceptan `factores` como lista JSON (multiselección Android) o como texto legado.

El botón SOS registra una alerta con `POST /api/v1/sos`. Una persona vinculada
puede consultar alertas activas recibidas con `GET /api/v1/sos/recibidas` y
responder mediante `PATCH /api/v1/sos/{alerta_id}`. Esto es una bandeja
consultable, no una notificación push: FCM no está conectado.

La vista de Mi Red obtiene horas y porcentaje de relevos completados durante el
mes con `GET /api/v1/contactos/usuarios/{id}/balance`. El calendario obtiene las
horas de solicitudes aceptadas o completadas de la semana con
`GET /api/v1/relevos/resumen/semana`.
El inicio consulta `GET /api/v1/checkins/tendencia`, que sugiere pedir apoyo si
hay carga alta en al menos tres días distintos de los últimos cinco; es una
regla preventiva simple, no un diagnóstico.

Se incluye `postman/RedCuidadora.postman_collection.json` con pruebas de
registro/login, perfil, check-in, red, relevo y SOS. Importa la colección y
configura variables locales: `base_url`, `correo`, `password`, `helper_email` y
`helper_password`. No uses credenciales reales en archivos versionados; para
MySQL y `JWT_SECRET`, configura los secretos en el entorno de despliegue.

En despliegue, termina TLS/HTTPS en un proxy inverso con certificado válido
(por ejemplo, el proxy configurado en 1Panel); no publiques directamente el
puerto HTTP del contenedor a Internet. HTTPS cifra el transporte, pero no
sustituye los tokens ni la autorización. `/health` solo confirma que el proceso
HTTP responde; no verifica que MySQL esté disponible.

El lifespan aplica primero `alembic upgrade head` y después
`Base.metadata.create_all`. Esto automatiza el esquema para el arranque, pero
en producción se debe probar la migración con backup y considerar que varios
workers arrancando a la vez pueden competir por migrar. Los errores no
controlados responden JSON genérico 500; el detalle real se reserva a logs
internos para no filtrar SQL, credenciales ni rutas del servidor.

La documentación interactiva y el esquema OpenAPI están deshabilitados en el
servidor para no publicar un explorador de rutas. La comprobación de salud queda
en `/health`. Las rutas principales están bajo `/api/v1/usuarios`,
`/api/v1/auth`, `/api/v1/perfil`, `/api/v1/checkins`, `/api/v1/contactos`,
`/api/v1/relevos` y `/api/v1/sos`; `GET /hello` devuelve `Hello World` como
consulta pública solicitada para la evaluación.
No existe un endpoint para listar todos los usuarios: se retiró para evitar
enumerar públicamente correos, códigos y perfiles.

## Formalización Técnica

* **Definición del Problema:** Dificultad en el acceso oportuno a recursos de apoyo psicosocial y orientación en salud mental a nivel comunitario, lo que genera desinformación, barreras de atención y falta de seguimiento en los usuarios.
* **Stack Tecnológico:**
  * **Frontend Móvil:** Android Studio / Flutter / Figma (Multiplataforma)
  * **Backend API:** 
  * **Base de Datos:**   (Normalizada)
  * **Control de Versiones:** Git & GitHub (Flujo Gitflow)
* **Justificación Técnica:** 
* **User Flow:** 

# Propuesta de Proyecto: RedCuidadora

## Concepto General y Propuesta de Valor
**RedCuidadora** es una aplicación diseñada para que las personas cuidadoras organicen y activen su red de apoyo antes de que la sobrecarga derive en una crisis. Está pensada para ser desarrollada de manera realista por estudiantes de Técnico en Computación e Informática. No busca diagnosticar con inteligencia artificial, crear una plataforma masiva de voluntariado ni funcionar como un sistema de citas o coincidencias entre desconocidos.

* **Definición del problema:** Las personas cuidadoras dependen de familiares, amigos y vecinos para recibir apoyo, pero esta ayuda se coordina de manera informal y suele concentrarse en una sola persona, lo que dificulta el descanso e incrementa el agotamiento.
* **Solución:** Organizar y activar la red existente del cuidador, facilitando solicitudes concretas, distribución equitativa de los relevos y seguimiento del nivel de carga.
* **Concepto central:** Hacer visible la sobrecarga y facilitar que la propia red intervenga antes del colapso emocional o físico.

---

## Pilares Fundamentales de la Aplicación

### 1. Detección simple de la sobrecarga
El usuario registra de forma periódica su estado mediante opciones sencillas:
* Estoy bien
* Estoy cansado/a
* Necesito apoyo
* Estoy sobrepasado/a

También puede registrar situaciones cotidianas específicas:
* Dormí mal
* No pude descansar
* Tengo que hacer un trámite
* Necesito salir por un rato
* Necesito compañía
* Necesito que alguien releve el cuidado

> *Con estos datos, la aplicación calcula y muestra una tendencia de carga de cuidado sin emitir diagnósticos médicos o psicológicos.*

### 2. Activación del círculo de confianza
El usuario configura su red privada con personas de su entorno cercano (**Familia → Amigos → Vecinos de confianza**).

* **Ejemplo de red:** Ana (hermana), Pedro (hijo), Carla (vecina), Juan (amigo).
* **Configuración de disponibilidad:** Cada integrante especifica sus horarios y el tipo de ayuda en que puede colaborar *(Ejemplo: Pedro está disponible martes y jueves de 18:00 a 20:00 para acompañamiento, compras o relevos)*.
* **Enfoque:** Se enfoca en organizar a los contactos que ya existen en la vida del cuidador, omitiendo la interacción con desconocidos en internet para mantener el proyecto realista.

### 3. Transformación de necesidades en solicitudes concretas
Convierte requerimientos generales en acciones puntuales y claras.

* **Tipos de ayuda seleccionables:** Necesito descansar, Necesito hacer compras, Necesito ir a una consulta, Necesito que alguien releve el cuidado, Necesito conversar, Necesito ayuda con un trámite.

**Flujo de solicitud:**
1. El usuario selecciona la necesidad *(Ejemplo: "Necesito descansar")*.
2. Define fecha y hora *(Ejemplo: Jueves 17:00–18:00)*.
3. Envía la solicitud a su red.
4. Los miembros reciben una notificación puntual:
   > *"María necesita un relevo de 1 hora este jueves. ¿Puedes ayudar?"*  
   > `[Puedo ayudar]` `[No puedo]`
5. La aplicación registra qué persona aceptó.

---

## Factor de Innovación y Diferenciación
A diferencia de aplicaciones de mensajería como WhatsApp, que se limitan a la conversación, **RedCuidadora** gestiona y visibiliza la distribución de las tareas de cuidado.

* **Visibilidad de la carga:** La app muestra el historial de apoyo recibido *(Ejemplo: Ana ayudó 3 veces este mes, Pedro 1 vez, Carla 0 veces, Juan 2 veces)*.
* **Sugerencia de equilibrio:** Si el sistema detecta que un solo integrante asume la mayoría de la ayuda *(Ejemplo: "El 65% de las solicitudes de este mes fueron atendidas por Ana")*, notificará al usuario:
  > *"Tu red tiene otras personas disponibles. ¿Quieres distribuir las próximas solicitudes?"*
* **Exclusión de gamificación:** Se descarta el uso de puntos o créditos *(del tipo "ayudaste 5 veces = tienes 5 créditos")*, evitando tratar el cuidado como un banco de favores o una competencia. La ayuda no se paga; la app únicamente la visibiliza y organiza.

---

## Funcionalidad de Emergencia: SOS de Confianza

Si el usuario indica el nivel máximo de sobrecarga (*"Estoy sobrepasado/a"* / *"Necesito apoyo ahora"*), la aplicación activa una alerta prioritaria dirigida únicamente a su círculo cercano.

> 🚨 **Mensaje de alerta:**  
> *"María necesita apoyo. Ha indicado que necesita ayuda inmediata. ¿Puedes comunicarte con ella?"*  
> `[Sí, puedo ayudar]` `[No puedo]`

* **Alcance del MVP:** Se excluyen el acceso público, la geolocalización exacta, las redes comunitarias abiertas y la verificación de domicilios en la primera etapa para no sobrecomplicar el desarrollo técnico.

## Anticipación al Agotamiento (Aporte Complementario)
La aplicación monitorea la tendencia de los registros continuos del usuario para sugerir acciones preventivas.

* **Ejemplo de registro continuo:**  
  `Lunes (Cansado/a)` → `Martes (Cansado/a)` → `Miércoles (Necesito apoyo)` → `Jueves (Necesito apoyo)` → `Viernes (Sobrepasado/a)`

> 🤖 **Acción del sistema:**  
> *"Has registrado varios días de alta carga. ¿Quieres solicitar apoyo a tu red?"*  
> *(Es una lógica simple de programar que aporta un alto valor preventivo).*

---

## Flujo de Funcionamiento del Producto Mínimo Viable (MVP)

1. Registro de usuario.
2. Creación del perfil del cuidador.
3. Creación del círculo de confianza.
4. Registro del estado/carga diaria.
5. Cálculo y visualización del nivel de carga.
6. Creación de una solicitud de ayuda específica.
7. Selección de fecha y horario.
8. Envío de la solicitud a la red.
9. Aceptación por parte de un integrante.
10. Registro del relevo en el sistema.
11. Actualización del historial de carga y apoyo recibido.

---

## Arquitectura y Alcance Técnico para Estudiantes

### Pantallas Requeridas (Versión 1)
* Inicio de sesión / Registro
* Pantalla de inicio
* Registro de estado emocional / Carga
* Creación de solicitud de ayuda
* Mi red de apoyo
* Solicitudes recibidas
* Calendario de relevos
* Historial de apoyo
* Perfil de usuario

### Componentes Tecnológicos
* Frontend móvil o web.
* Base de datos relacional o no relacional.
* Módulo de gestión y autenticación de usuarios.
* Lógica para relaciones entre usuarios (cuidador y red).
* Módulo de creación y cambio de estado en solicitudes.
* Sistema de notificaciones.
* Lógica condicional básica para determinar la tendencia de carga *(sin necesidad de modelos de IA)*.

---

## Estrategia de Presentación Recomendada

* **Estructura del proyecto:** Utilizar la propuesta principal como la base de la solución y los componentes de seguimiento como complemento preventivo.
* **Fase inicial:** Definir detalladamente la problemática, el usuario objetivo, la propuesta de valor, la innovación respecto a herramientas tradicionales y el MVP antes de iniciar la etapa de programación o diseño de pantallas.
