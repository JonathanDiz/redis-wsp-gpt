#ChatBot inteligente con WhatsApp en Python
from flask import Flask, jsonify, request
from twilio.twiml.messaging_response import MessagingResponse
import redis
import datetime

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)

respuesta = MessagingResponse()
respuesta.message(request.form.get("Body"))
mensaje_enviado = respuesta.to_xml().decode("utf-8")
r.hset("whatsapp_mensajes", "mensaje_enviado", mensaje_enviado)


#RUTA DE HOME
@app.route('/', methods=['GET', 'POST'])
def home():
   return "HELLO from vercel use flask"

#CUANDO RECIBAMOS LAS PETICIONES EN ESTA RUTA
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    #SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        #SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "HolaChatbotGPT":
            #ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            #SI NO SON IGUALES RETORNAMOS UN MENSAJE DE ERROR
          return "Error de autentificacion."
    #RECIBIMOS TODOS LOS DATOS ENVIADO VIA JSON
    data=request.get_json()
    #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
    telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    #EXTRAEMOS EL TELEFONO DEL CLIENTE
    mensaje_data=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
    idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
    timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO
    #SI HAY UN MENSAJE
    if mensaje_data is not None:
      from rivescript import RiveScript
      #INICIALIZAMOS RIVESCRIPT Y CARGAMOS LA CONVERSACION
      bot = RiveScript()
      bot.load_file('restaurante.rive')
      bot.sort_replies()
      #OBTENEMOS LA RESPUESTA
      respuesta= bot.reply("localuser", mensaje_data)
      respuesta= respuesta.replace("\\n", "\\\n")
      respuesta= respuesta.replace("\\","")

      #CONECTAMOS A BASE DE DATOS REDIS
      redis_host = redis_host.env.REDIS_HOST
      redis_port = redis_port.env.REDIS_PORT
      redis_password = redis_password.env.PASSWORD

      redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

      #CONFIGURACION REGISTRO REDIS
      id = 1
      fecha_hora = datetime.datetime.now().date() + " " + datetime.datetime.now().time()
      mensaje_recibido = mensaje_data.replace("\n", "\\n")
      mensaje_enviado = respuesta.replace("\\n", "\\\n")
      id_wsp = idWA
      timestamp_wsp = timestamp
      telefono_wsp = telefonoCliente

      redis_conn.hset("registro:" + str(id), "id", id)
      redis_conn.hset("registro:" + str(id), "fecha_hora", fecha_hora)
      redis_conn.hset("registro:" + str(id), "mensaje_recibido", mensaje_recibido)
      redis_conn.hset("registro:" + str(id), "mensaje_enviado", mensaje_enviado)
      redis_conn.hset("registro:" + str(id), "id_wsp", id_wsp)
      redis_conn.hset("registro:" + str(id), "timestamp_wsp", timestamp_wsp)
      redis_conn.hset("registro:" + str(id), "telefono_wsp", telefono_wsp)

      f = open("texto.txt", "w")
      f.write(mensaje_data + "\n")
      f.close()
      #RETORNAMOS EL STATUS EN UN JSON
      return jsonify({"status": "success"}, 200)

#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)