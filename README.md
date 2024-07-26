# User Group Chatbot - GenIA BedrockAgent Claude

Este proyecto contiene un chatbot para grupos de usuarios, basado en la arquitectura GenIA BedrockAgent Claude.

## Contenido

- `CODE_OF_CONDUCT.md`: Código de conducta del proyecto.
- `LICENSE`: Licencia del proyecto.
- `test.json`: Archivo de prueba.
- `.gitignore`: Archivos y directorios a ignorar por git.
- `CONTRIBUTING.md`: Guía para contribuir al proyecto.
- `private-assistant`: Contiene el código fuente del asistente privado.
  - `lambdas`: Funciones Lambda.
  - `databases`: Configuración y scripts de bases de datos.
  - `bedrock_agents`: Definición del agente de Bedrock.
  - `apis`: Definiciones y configuraciones de APIs.
  - `layers`: Capas utilizadas por las funciones Lambda.
  - `private-assistant`: Contiene el root de las definiciones de la infraestructura.
  - `requirements.txt`: Dependencias del proyecto.
  - `tests`: Pruebas del proyecto.
  - `app.py`: Archivo principal de la aplicación.

## Instalación

Para instalar y desplegar la infraestructura del proyecto utilizando AWS CDK, sigue estos pasos:

1. Clona el repositorio:
   ```sh
   git clone https://github.com/hsaenzG/whatsapp_user_group_chatbot_genia_bedrock_agent_claude_serverless.git
   ```
2. Navega al directorio del proyecto:
   ```sh
   cd whatapp-usergroup-chat-bedrock-claude-serverless/private-assistant
   ```
3. Instala las dependencias necesarias:
   ```sh
   pip install -r requirements.txt
   ```
4. Instala AWS CDK:
   ```sh
   npm install -g aws-cdk
   ```
5. Inicializa el entorno de CDK:
   ```sh
   cdk bootstrap
   ```
6. Inicializa el entorno de CDK:
   ```sh
   cdk bootstrap
   ```
7. Modifica el no de telefono que utilizaras en Whatsapp, en el archivo provate_assitant--> private_asistant_stack.py:
   ```sh
    DISPLAY_PHONE_NUMBER = 'XXXXXXXXXX' <- Tu numero de telefono a utilizar 
   ```
## Agradecimientos
   Este repositorio se tomo de base del proyecto de Elizabeth Fuentes (https://github.com/elizabethfuentes12), gracias por tu excelente aporte a la comunidad, tu articulo fue una guia vital para la rapida implementación de este proyecto.  
    <br/> Si tienes dudas de como configurar la integración con WhatsApp utiliza la siguiente documentación:
    <br/>repo: https://github.com/build-on-aws/building-gen-ai-whatsapp-assistant-with-amazon-bedrock-and-python
    <br/>Articulo: https://dev.to/aws-espanol/construyendo-un-asistente-genai-de-whatsapp-con-amazon-bedrock-2hid

## Seguridad

Ve: [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) para mas información.

## Licencia

Esta libreria esta bajo una licencia MIT-0. 
