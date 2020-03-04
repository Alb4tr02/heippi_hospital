# Heippi Hospital RESTFUL API
<p align="center"> <img src="Logo_Heippi_Hospital.png"/> </p>
This repository is cretae to Heippi Backend Developer - Prueba técnica

**Reto**: Desarrollo de servicio web (API REST) que sirva endpoints para un sistema de gestión de
historia clínica centralizada.

**NOTA**: Este es un proyecto que evaluaremos como si fuera real aunque sea ficticio, no es necesario
enviar proyecto. Solo requerimos llamada virtual para recibir indicaciones de lo realizado.

**Requerimientos**:

**1** Permitir registro de usuarios con Identificación, Email, Teléfono y
contraseña.**Condiciones**: Los tipos de usuario permitidos en registro son Hospital y Paciente.

**4** Registro de datos básicos de usuario:
Si el usuario es de tipo Hospital debe registrar: Nombre, Dirección, Servicios
médicos que brinda.
Si el usuario es de tipo paciente debe registrar: Nombre, Dirección, fecha de
nacimiento.

**Solución**:

**Signin pacients**  

route: "/new-pacient/add"  
methods allowed: POST  
parameters: usr_cc, usr_email, usr_phone, usr_password, usr_name, [usr_addr], [usr_birth_date]  
Curl Example:  
curl -d "usr_cc=00001&usr_email=jodmunozol@unal.edu.co&usr_phone=1234&usr_password=123456&usr_name=Johan" -X POST http://localhost:3000/new-pacient/add  

**Signin hospitals**  
route: "/new-hospital/add"  
methods allowed: POST  
parameters: hosp_cc, hosp_email, hosp_phone, [hosp_services], hosp_name, [hosp_addr]  
Curl Example:  
curl -d "hosp_cc=00002&hosp_name=Heippi Hospital&hosp_email=834@holbertonschool.com&hosp_phone=1234&hosp_pass	word=123456" -X POST http://localhost:3000/new-hospital/add  

**2** Confirmación de registro por parte de usuario a través de uno de sus datos de
contacto.**Condiciones**: El usuario no podrá acceder al sistema hasta que confirme su registro.

Solución: Cuando se utiliza el sign in para crear un usuario nuevo automaticamente se envía un correo para confirmar el registro  


3 Inicio de sesión de usuario utilizando Identificación y Contraseña.

**Solución**  
**Loggin**  
route: "/login"  
methods allowed: POST  
parameters: cc, password  
Notes: In order to access you must verify your email address, and then if you are trying to loggin as doctor you have to reset your default password  
Curl Example:  
curl -d "cc=00002&password=123456" -X POST http://localhost:3000/loggin

**5** Registro de usuario tipo Médico por parte de un usuario Hospital. Condiciones:
Condiciones similares al registro de los otros tipos de usuario.  
La primera vez que inicie sesión debe cambiar la contraseña y establecer una nueva
contraseña.
**Solución**: A los usuarios tipo médico al confirmar su correo, les llega un nuevo correo con una URL para realizar  el cambio de contraseña por defecto que les asigna el hospital, los usurios tipo médico no podrán realizar ninguna acción hasta que no cambien su contraseña por defecto

**Create new doctors**  
route: "/new-doctor/add"  
methods allowed: POST  
parameters: doc_cc, doc_email, doc_phone, doc_password, [doc_name]  
Notes: In order to create a new doctor user, you must be logged as hospital user  
Curl Example:  
curl -d "doc_cc=00003&doc_password=123456&doc_email=942@holbertonschool.com&doc_phone=1234" -X POST http://localhost:3000/new-doctor/add  

**6** Todos los usuarios deben cambiar y/o recuperar su contraseña cuando lo deseen.  
**Reset password**  
route: "/account/reset-password"  
methods allowed: POST  
parameters: cc  
Curl Example:  
curl -d "cc=00001" -X POST http://localhost:3000/account/reset-password  

Actualización de datos opcionales para cada tipo de usuario:

**Update pacient data**  
route: "/pacient/update"  
methods allowed: PUT  
parameters: [usr_date_birth], [usr_name], [usr_addr]  
Notes: In order to update the data you must be logged as pacient user  
Curl Example:  
curl -d "usr_name=tonytony" -X PUT http://localhost:3000/pacient/update  

**Update Hospital data**  
route: "/hospital/update"  
methods allowed: PUT  
parameters: [hosp_services], [hosp_name], [hosp_addr]  
Notes: In order to update the data you must be logged as hospital user  
Curl Example:  
curl -d "hosp_services=surgery, rehabilitation&hosp_name=Arkham Asylum" -X PUT http://localhost:3000/hospital/update  

**Update Doctor data**  
route: "/doctor/update"  
methods allowed: PUT  
parameters: [doc_name]  
Notes: In order to update the data you must be logged as doctor user  
Curl Example:  
curl -d "doc_name=Bruce Wayne" -X PUT http://localhost:3000/doctor/update

**7** Permitir a un usuario de Tipo Médico registrar observaciones médicas y estado de salud
de un usuario de tipo Paciente. Condiciones: Obligatorio indicar especialidad médica brindada al Paciente  
**Create medical observations**  
route: "/medical-observations"  
methods allowed: GET  
parameters: health, observations, especiality, usr_cc  
Notes: In order to create a new medical observation you must be logged as doctor user  
Curl Example:  
curl -d "health=bad&usr_cc=00001&observations=pacient have flu&especiality=homeopathy" -X POST http://localhost:3000/medical-observations/add  

**8** Cualquier usuario debe poder consultar todos los registros de observaciones médicas  
registradas. Condiciones:  
Mostrar: hospital, médico, especialidad y detalle de cada registro asociado al
paciente.  
Usuario Paciente, solo puede consultar sus registros.  
Usuario Médico, puede consultar registros realizados por él mismo.  
Usuario Hospital, puede consultar los registros realizados por sus Médicos.  

**Get medical observations**
route: "/medical-observations"
methods allowed: GET
parameters: none
Notes: response sended in Json format
Curl Example:
curl http://localhost:3000/medical-observations

**9** Descargar archivo con todas las observaciones de un Paciente registradas en el sistema.Condiciones iguales al punto 7

**Get medical observations pdf format**
route: "/medical-observations/<cc>"
methods allowed: GET
parameters: cc represents the id of the pacient
Notes: In order to get a pdf file filled with the patient's medical history, you must be logged as doctor user
Curl Example:
curl -o file_name.pdf http://localhost:3000/medical-observations/00001 