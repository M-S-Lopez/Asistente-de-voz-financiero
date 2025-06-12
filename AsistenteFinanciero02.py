import pyttsx3  # convierte texto en voz
import speech_recognition as sr # convertir voz en texto
import datetime # manipular fechas y horas 
import webbrowser # permite abrir páginas web directamente en el navegador
import yfinance as yf # obtiene datos financieros de Yahoo Finance
import ccxt # interactua con múltiples exchanges de criptomonedas, podemos consultar precios, balances, ejecutar órdenes, etc
import requests # solicitudes HTTP
import translate # traductor de python

# Opciones de voz / idioma
id1 = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
id2 = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
id3 = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0"

# Tus claves de API
api_key = ''
api_secret = ''

# Obtener precio
def obtener_precio(criptomoneda):
    exchange = ccxt.binance()  # elegimos la plataforma que queremos usar
    ticker = exchange.fetch_ticker(criptomoneda + '/USDT')  # nos trae el precio de la cripto en usdt
    return ticker['last']

# Obtener saldo actual 
def obtener_saldo_binance(api_key, api_secret): # obtenemos el saldo de una cuenta de binance
    exchange = ccxt.binance({
        'apiKey': api_key, 
        'secret': api_secret,
        # le pasamos los datos de la cuenta a traves de las claves 
    })

    # Cargar mercados y obtener balances
    exchange.load_markets()

    # Obtener el balance de la cuenta 'spot' por defecto
    balance = exchange.fetch_balance()

    # Filtrar y mostrar solo las monedas con saldo positivo
    saldo_total = {moneda: cantidad for moneda, cantidad in balance['total'].items() if cantidad > 0}
    
    return saldo_total

# Informacion de una determinada crypto usando al API de CoinGecko
def obtener_info_proyecto(crypto_id):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}" 
    respuesta = requests.get(url) #hacemos una peticion a la BD de la web
    if respuesta.status_code == 200: # si devuelve un 200, encontro lo que buscaba 
        return respuesta.json() # y nos devuelve un json
    else:
        return None

# Transformar audio a texto
def transformar_audio_texto():
    # Almacenar recognizer en variable
    r = sr.Recognizer()

    # Configurar el microfono
    with sr.Microphone() as origen:
        # Tiempo de espera
        r.pause_threshold = 0.8

        # Informar que comenzo la grabacion
        print("Ya puedes hablar")

        # Guardar el audio
        audio = r.listen(origen)

        try:
            # Buscar en google
            pedido = r.recognize_google(audio, language="es-ES")

            # Imprimir prueba de ingreso
            print(f"Dijiste: {pedido}")

            # Devolver pedido
            return pedido
        except sr.UnknownValueError:
            # Prueba de que no comprendió audio
            print("Ups, no entendí")
            return "Sigo esperando"
        except sr.RequestError:
            # Prueba de que no comprendió audio
            print("Ups, no hay servicio")
            return "Sigo esperando"
        except:
            # Prueba de que no comprendió audio
            print("Ups, algo ha salido mal")
            return "Sigo esperando"

# Función para que el asistente pueda ser escuchado
def hablar(mensaje):
    # Encender el motor de pyttsx3
    engine = pyttsx3.init()
    engine.setProperty("voice", id3)

    # Pronunciar mensaje
    engine.say(mensaje)
    engine.runAndWait()

# Función saludo inicial
def saludo_inicial():
    # Crear variable con datos de hora
    hora = datetime.datetime.now()

    if hora.hour < 6 or hora.hour > 20:
        momento = "Buenas noches"
    elif 6 <= hora.hour < 13:
        momento = "Buen día"
    else:
        momento = "Buenas tardes"

    # Decir saludo
    hablar(f"{momento} en qué te puedo ayudar?")

# Función central del asistente
def centro_pedido():
    # Saludo inicial
    saludo_inicial()

    # Variable de corte
    comenzar = True

    while comenzar:
        # Activar el micrófono y guardar el pedido en un String
        pedido = transformar_audio_texto().lower()

        print(f"Comando recibido: {pedido}")

        if "precio de la criptomoneda" in pedido or "quiero el precio de la criptomoneda" in pedido or "dame el precio de la criptomoneda" in pedido:
            cripto = pedido.split("criptomoneda")[-1].strip().lower() # el -1 es para escuchar despues de criptomoneda  (ya sea bitcoin, etherium, etc)
            # guarda esa cripto en la var cripto y la busca en la cartera
            cartera = {
                "bitcoin": "BTC",
                "ethereum": "ETH",
                "solana": "SOL",
                "cardano": "ADA",
                "hondo": "ONDO"
            }
            try:
                cripto_buscada = cartera[cripto]
                precio_actual = obtener_precio(cripto_buscada)
                hablar(f"El precio actual de {cripto} es {precio_actual} dólares.")
            except KeyError:
                hablar(f"No tengo información sobre la criptomoneda {cripto}.")
            except Exception as e:
                hablar("Perdón, pero no pude encontrar la información de la criptomoneda.")
                print(e)
            continue
        elif "decime mi saldo actual en spot" in pedido or "saldo actual en spot" in pedido or "cual es mi saldo actual en spot" in pedido:
            # Obtener el saldo filtrado
            saldo = obtener_saldo_binance(api_key, api_secret)
            # Mostrar el saldo total filtrado
            if saldo:
                print("Tus saldos disponibles:")
                hablar(f"Tus saldos disponibles en billetera SPOT son")
                for moneda, cantidad in saldo.items():
                    print(f"{moneda}: {cantidad}")
                    hablar(f"{moneda}: {cantidad}")
            else:
                hablar("No tienes saldo disponible en ninguna criptomoneda.")
            continue
        elif "descripción de la criptomoneda" in pedido or "quiero de una descripción de la criptomoneda" in pedido or "dame una descripción de la criptomoneda" in pedido:
            cripto = pedido.split("criptomoneda")[-1].strip().lower() #el -1 es para que escuche lo que viene despues de criptomoneda (como bitcoin, etherium, solana )
            # y guarda esa cripto para busarla despues
            info = obtener_info_proyecto(cripto)
            text = info['description']['en']
            if text:
                target_language = "es"
                translator = translate.Translator(to_lang=target_language)
                translated_text = translator.translate(text)
                print(f"Descripción: {translated_text}")
                hablar(translated_text)
            else:
                hablar(f"No se encontró descripción de la criptomoneda {cripto}.")
            continue
        elif "abre página del proyecto" in pedido or "redirige a la página del proyecto" in pedido or "página del proyecto" in pedido: 
            #nos lleva a la pagina de inicio de las criptos
            
            cripto = pedido.split("proyecto")[-1].strip().lower()
            info = obtener_info_proyecto(cripto)
            pagina_web = info['links']['homepage'][0]
            if pagina_web:
                hablar("No hay problema")
                webbrowser.open(pagina_web)
            else:
                hablar(f"No se encontró página web del proyecto {cripto}.")
            continue
        elif "precio de la acción de" in pedido or "quiero el precio de la acción de" in pedido or "dame el precio de la acción de" in pedido or "quiero saber el precio de la accion de" in pedido:
            accion = pedido.split("de")[-1].strip().lower()
            cartera = {
                "apple": "AAPL",
                "amazon": "AMZN",
                "google": "GOOGL",
                "tesla": "TSLA",
                "mcdonald's": "MCD",
                "facebook": "META"
            }
            try:
                accion_buscada = cartera[accion]
                ticker = yf.Ticker(accion_buscada)
                # precio_actual = ticker.info['regularMarketPrice']
                # Obtener el último precio disponible
                hist = ticker.history(period="1d")  # Datos del último día
                precio_actual = hist['Close'][0]  # Precio de cierre del día
                hablar(f"La encontré, el precio de {accion} es {precio_actual} dólares.")
            except KeyError:
                hablar(f"No tengo información sobre la acción de {accion}.")
            except Exception as e:
                hablar("Perdón, pero no pude encontrar la información de la acción.")
                print(e)
            continue
        elif "cuál es el sector de la empresa" in pedido or "sector de la empresa" in pedido or "quiero saber cual es el sector de la empresa" in pedido:
            empresa = pedido.split("empresa")[-1].strip().lower()
            cartera = {
                "apple": "AAPL",
                "amazon": "AMZN",
                "google": "GOOGL",
                "tesla": "TSLA",
                "mcdonald's": "MCD",
                "facebook": "META"
            }
            try:
                empresa_buscada = cartera[empresa]
                ticker = yf.Ticker(empresa_buscada)
                info_empresa = ticker.info
                sector = info_empresa['sector']
                print(f"Sector: {sector}")
                target_language = "es"
                translator = translate.Translator(to_lang=target_language)
                translated_text = translator.translate(sector)
                hablar(f"El sector de la empresa {empresa} es: {translated_text}")
            except KeyError:
                hablar(f"No tengo información sobre la empresa {empresa}.")
            except Exception as e:
                hablar("Perdón, pero no pude encontrar la información de la empresa.")
                print(e)
            continue
        elif "cuál es la industria de la empresa" in pedido or "industria de la empresa" in pedido or "quiero saber cual es la industria de la empresa" in pedido:
            empresa = pedido.split("empresa")[-1].strip().lower()
            cartera = {
                "apple": "AAPL",
                "amazon": "AMZN",
                "google": "GOOGL",
                "tesla": "TSLA",
                "mcdonald's": "MCD",
                "facebook": "META"
            }
            try:
                empresa_buscada = cartera[empresa]
                ticker = yf.Ticker(empresa_buscada)
                info_empresa = ticker.info
                industria = info_empresa['industry']
                print(f"Industria: {industria}")
                target_language = "es"
                translator = translate.Translator(to_lang=target_language)
                translated_text = translator.translate(industria)
                hablar(f"La industria de la empresa {empresa} es: {translated_text}")
            except KeyError:
                hablar(f"No tengo información sobre la empresa {empresa}.")
            except Exception as e:
                hablar("Perdón, pero no pude encontrar la información de la empresa.")
                print(e)
            continue
        elif "cuál es la capitalización de mercado de la empresa" in pedido or "capitalización de mercado de la empresa" in pedido or "quiero saber cual es la capitalización de mercado de la empresa" in pedido:
            empresa = pedido.split("empresa")[-1].strip().lower()
            cartera = {
                "apple": "AAPL",
                "amazon": "AMZN",
                "google": "GOOGL",
                "tesla": "TSLA",
                "mcdonald's": "MCD",
                "facebook": "META"
            }
            try:
                empresa_buscada = cartera[empresa]
                ticker = yf.Ticker(empresa_buscada)
                info_empresa = ticker.info
                market_cap = info_empresa['marketCap']
                print(f"Capitalización de mercado: {market_cap}")
                hablar(f"La capitalización de mercado de la empresa {empresa} es: {market_cap}")
            except KeyError:
                hablar(f"No tengo información sobre la empresa {empresa}.")
            except Exception as e:
                hablar("Perdón, pero no pude encontrar la información de la empresa.")
                print(e)
            continue
        elif "cuál es la cantidad de acciones en circulación de la empresa" in pedido or "cantidad de acciones en circulación de la empresa" in pedido or "quiero saber cual es la cantidad de acciones en circulación de la empresa" in pedido:
            empresa = pedido.split("empresa")[-1].strip().lower()
            cartera = {
                "apple": "AAPL",
                "amazon": "AMZN",
                "google": "GOOGL",
                "tesla": "TSLA",
                "mcdonald's": "MCD",
                "facebook": "META"
            }
            try:
                empresa_buscada = cartera[empresa]
                ticker = yf.Ticker(empresa_buscada)
                info_empresa = ticker.info
                acciones_en_circulacion = info_empresa['sharesOutstanding']
                print(f"Cantidad de acciones en circulación: {acciones_en_circulacion}")
                hablar(f"La cantidad de acciones en circulación de la empresa {empresa} es: {acciones_en_circulacion}")
            except KeyError:
                hablar(f"No tengo información sobre la empresa {empresa}.")
            except Exception as e:
                hablar("Perdón, pero no pude encontrar la información de la empresa.")
                print(e)
            continue
        elif "adiós" in pedido:
            hablar(f"Nos vemos, avisame si necesitas otra cosa ")
            break
            

centro_pedido()