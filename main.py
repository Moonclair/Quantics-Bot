import os
my_secret = os.environ['TOKEN']

import os
import discord
from discord.ext import commands, tasks
import datetime
import pytz
import asyncio

from keep_alive import keep_alive
keep_alive()


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name='cafe' , help='Soy un capricho de mi creador')
             
async def cafe(ctx):
  await ctx.send(f":coffee: para {ctx.author.mention}!")

@bot.command(name='matecocidoconleche', help='Soy un capricho de mistics')

async def matecocidoconleche(ctx):
  url_imagen = "https://i.ibb.co/mB3SzQ2/matecocido.jpg"
  await ctx.send(f"matecocido para {ctx.author.mention}! {url_imagen}")

# Definir la zona horaria UTC-3
zona_horaria_utc_menos_3 = pytz.timezone('America/Argentina/Buenos_Aires')

# Variables globales para almacenar la hora de la invasión más cercana y los mensajes enviados
inva_mas_cercana = None
mensaje_1h_enviado = False
mensaje_30min_enviado = False
mensaje_15min_enviado = False

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    # Iniciar la tarea para verificar y enviar mensajes
    check_time.start()

@bot.command()
async def inva(ctx):
    global inva_mas_cercana
    # Obtener la hora actual en UTC-3
    ahora = datetime.datetime.now(zona_horaria_utc_menos_3)

    # Establecer las horas objetivo a las 12:00, 18:00 y 00:00 del día siguiente en UTC-3
    hora_objetivo_06 = zona_horaria_utc_menos_3.localize(datetime.datetime(ahora.year, ahora.month, ahora.day, 6, 0))
    hora_objetivo_12 = zona_horaria_utc_menos_3.localize(datetime.datetime(ahora.year, ahora.month, ahora.day, 12, 0))
    hora_objetivo_18 = zona_horaria_utc_menos_3.localize(datetime.datetime(ahora.year, ahora.month, ahora.day, 18, 0))
    hora_objetivo_00 = zona_horaria_utc_menos_3.localize(datetime.datetime(ahora.year, ahora.month, ahora.day + 1, 0, 0))
  

    # Calcular la invasión más cercana
    invasiones = [hora_objetivo_06, hora_objetivo_12, hora_objetivo_18, hora_objetivo_00]
    inva_mas_cercana = min([invasion for invasion in invasiones if invasion > ahora], default=min(invasiones))

    # Calcular tiempo restante para la invasión más cercana
    tiempo_restante = inva_mas_cercana - ahora

    # Formatear el tiempo restante
    tiempo_formateado = format_tiempo_restante(tiempo_restante)

    # Responder al usuario que solicitó la información
    await ctx.send(f"Faltan {tiempo_formateado} para la invasión de dorados a las {inva_mas_cercana.strftime('%H:%M')}")

@tasks.loop(seconds=60)
async def check_time():
    global inva_mas_cercana, mensaje_1h_enviado, mensaje_30min_enviado, mensaje_15min_enviado
    if inva_mas_cercana is None:
        return

    # Obtener la hora actual en UTC-3
    ahora = datetime.datetime.now(zona_horaria_utc_menos_3)

    # Calcular tiempo restante para la invasión más cercana
    tiempo_restante = inva_mas_cercana - ahora

    # Verificar si ya pasó la invasión más cercana
    if tiempo_restante.total_seconds() <= 0:
        check_time.stop()

        # Restablecer las variables después de que pase la invasión
        mensaje_1h_enviado = False
        mensaje_30min_enviado = False
        mensaje_15min_enviado = False

        return

    # Verificar si falta 1 hora para la invasión y enviar el mensaje a todos los usuarios
    if tiempo_restante.total_seconds() <= 3600 and not mensaje_1h_enviado:
        await enviar_mensaje_global(f"Falta 1 hora para la invasión de dorados a las {inva_mas_cercana.strftime('%H:%M')}",
              canales=['1183469827730452541', '1183469155408683078']
        )
        mensaje_1h_enviado = True

    # Verificar si falta 30 minutos para la invasión y enviar el mensaje a todos los usuarios
    elif tiempo_restante.total_seconds() <= 1800 and not mensaje_30min_enviado:
        mensaje_30min_enviado = True
        # Enviar el mensaje solo en los canales específicos
        await enviar_mensaje_global(
            f"Faltan 30 minutos para la invasión de dorados a las {inva_mas_cercana.strftime('%H:%M')}",
            canales=['1183469827730452541', '1183469155408683078']
        )

    # Verificar si falta 15 minutos para la invasión y enviar el mensaje a todos los usuarios
    elif tiempo_restante.total_seconds() <= 900 and not mensaje_15min_enviado:
        mensaje_15min_enviado = True
        # Restar 15 minutos a la hora de la invasión más cercana
        hora_reunion = inva_mas_cercana - datetime.timedelta(minutes=15)
        # Enviar el mensaje solo en los canales específicos
        await enviar_mensaje_global(
            f"Nos reuniremos a las {hora_reunion.strftime('%H:%M')} para:\n"
            "- Reseteo de stats: [link](https://uruz.gg/usercp/resetstats)\n"
            "- Armado de partys\n"
            "- Planificación de rutas\n\n"
            "Te esperamos!",
            canales=['1183469827730452541', '1183469155408683078']
        )

def format_tiempo_restante(tiempo_restante):
    # Extraer días, horas y minutos del timedelta
    dias, segundos = divmod(tiempo_restante.seconds, 86400)
    horas, segundos = divmod(segundos, 3600)
    minutos = segundos // 60

    # Formatear el tiempo restante
    if tiempo_restante.days < 0:
        return "0 minutos"  # Si ya ha pasado la invasión
    elif tiempo_restante.days == 0 and horas == 0:
        return f"{minutos} minutos"  # Si faltan menos de 1 hora
    elif tiempo_restante.days == 0:
        return f"{horas} horas y {minutos} minutos"
    else:
        return f"{tiempo_restante.days} días, {horas} horas y {minutos} minutos"

async def enviar_mensaje_global(mensaje, canales=None):
    for guild in bot.guilds:
        for channel in guild.text_channels:
            # Verificar si se especificaron canales y si el canal actual está en la lista
            if canales and str(channel.id) not in canales:
                continue
            await channel.send(mensaje)





# Ejecutar el bot con el token proporcionado
bot.run(my_secret)
