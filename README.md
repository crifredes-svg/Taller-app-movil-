# Proyecto Taller App Móvil

## Integrantes del Equipo
* **Línea de Desarrollo:** (App Psicosocial)
* **Frontend & UI:** Cristian Flores
* **Backend & DBA:** Diego Anabalon
* **DevOps & Integración:** Cristian Fredes

## Formalización Técnica

* **Definición del Problema:** Dificultad en el acceso oportuno a recursos de apoyo psicosocial y orientación en salud mental a nivel comunitario, lo que genera desinformación, barreras de atención y falta de seguimiento en los usuarios.
* **Stack Tecnológico:**
  * **Frontend Móvil:** Android Studio / Flutter (Multiplataforma)
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