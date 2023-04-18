from flask import Flask, jsonify, request
import redis

app = Flask(__name__)

# CONECTAMOS A REDIS
redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

#CUANDO RECIBAMOS LAS PETICIONES EN ESTA RUTA
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    #SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        #SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "HolaNovato":
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
    mensaje=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
    idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
    timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO
    #SI HAY UN MENSAJE
    if mensaje is not None:
      from rivescript import RiveScript
      #INICIALIZAMOS RIVESCRIPT Y CARGAMOS LA CONVERSACION
      bot = RiveScript()
      bot.load_file('restaurante.rive')
      bot.sort_replies()
      #OBTENEMOS LA RESPUESTA
      respuesta= bot.reply("localuser",mensaje)
      respuesta=respuesta.replace("\\n","\\\n")
      respuesta=respuesta.replace("\\","")
      
      # AÑADIMOS LOS DATOS A REDIS
      cantidad = redis_db.get(idWA)
      if cantidad is None:
          redis_db.set(idWA, 1)
          
          # Insertamos los datos en Redis
          registro = {
              'mensaje_recibido': mensaje,
              'mensaje_enviado': respuesta,
              'id_wa': idWA,
              'timestamp_wa': timestamp,
              'telefono_wa': telefonoCliente
          }
          redis_db.hmset(idWA, registro)
      else:
          # Actualizamos la cantidad
          cantidad = int(cantidad) + 1
          redis_db.set(idWA, cantidad)
          
      #RETORNAMOS EL STATUS EN UN JSON
      return jsonify({"status": "success"}, 200)

#INICIAMSO FLASK
if __name__ == "__main__":
   app.run(debug=True)
