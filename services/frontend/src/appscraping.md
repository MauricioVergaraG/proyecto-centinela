### **Proyecto: Reddit Comment Scraper**

**Objetivo:** Crear una aplicación web mínima funcional que permita al usuario introducir un subreddit y una palabra clave, y luego muestre una lista de comentarios de Reddit que coincidan con esa búsqueda.

**Tecnologías:**
*   **Python 3:** Lenguaje de programación.
*   **Flask:** Microframework web para Python.
*   **PRAW (Python Reddit API Wrapper):** Librería para interactuar con la API de Reddit.
*   **HTML/CSS:** Para la interfaz de usuario.

---

### **Paso 0: Preparación del Entorno**

Antes de empezar a codificar, necesitamos preparar tu entorno de desarrollo.

1.  **Instalar Python:** Asegúrate de tener Python 3 instalado en tu sistema. Puedes descargarlo de [python.org](https://www.python.org/downloads/).

2.  **Crear una Carpeta para tu Proyecto:**
    Crea una carpeta en tu computadora donde guardarás todos los archivos de tu proyecto. Por ejemplo, `reddit_scraper_project`.

3.  **Abrir la Terminal/Línea de Comandos:**
    Navega a la carpeta de tu proyecto usando la terminal (cmd, PowerShell en Windows; Terminal en macOS/Linux).

    ```bash
    cd ruta/a/tu/reddit_scraper_project
    ```

4.  **Crear un Entorno Virtual (¡Muy Importante!):**
    Un entorno virtual aísla las dependencias de tu proyecto de otras instalaciones de Python. Esto evita conflictos y mantiene tu proyecto limpio.

    ```bash
    python -m venv venv
    ```
    *(Esto crea una carpeta llamada `venv` dentro de tu proyecto, que contendrá el entorno virtual.)*

5.  **Activar el Entorno Virtual:**

    *   **En Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **En macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    *(Verás `(venv)` al principio de tu línea de comandos, indicando que el entorno virtual está activo.)*

6.  **Instalar las Librerías Necesarias:**
    Ahora que el entorno virtual está activo, instala Flask y PRAW.

    ```bash
    pip install Flask praw
    ```

---

### **Paso 1: Configuración de la API de Reddit (PRAW)**

Para que tu aplicación pueda "hablar" con Reddit, necesitas obtener credenciales de la API.

1.  **Ve a Reddit Apps:** Abre tu navegador y ve a [https://www.reddit.com/prefs/apps/](https://www.reddit.com/prefs/apps/).

2.  **Crea una Nueva Aplicación:** Haz clic en el botón "are you a developer? create an app...".
    *   **Elige `script` como tipo de aplicación.**
    *   **Name:** Dale un nombre a tu aplicación (ej. `MiScraperUniversitario`).
    *   **Description:** Una breve descripción (ej. `Aplicación universitaria para web scraping de comentarios`).
    *   **redirect uri:** Pon `http://localhost:8080` (esto es importante aunque no lo usemos directamente para este tipo de aplicación, Reddit lo requiere).
    *   Deja los otros campos en blanco o por defecto.

3.  **Obtén tus Credenciales:** Una vez que crees la aplicación, verás una sección para ella. Necesitarás estos dos valores:
    *   **`client_id`**: Está justo debajo del nombre de tu aplicación. Es una cadena de caracteres alfanuméricos.
    *   **`client_secret`**: Haz clic en "edit" al lado de tu aplicación, y el "secret" será visible. También es una cadena alfanumérica.

    **Guarda estos dos valores en un lugar seguro. ¡No los compartas públicamente!**

---

### **Paso 2: Creación de la Aplicación Flask y Lógica de Scraping**

Ahora, vamos a escribir el código Python para tu aplicación.

**Dentro de tu carpeta `reddit_scraper_project`, crea un archivo llamado `app.py`.**

```python
# app.py

# ============================ 1. Importar Librerías ============================
import praw # Para interactuar con la API de Reddit
from flask import Flask, render_template, request # Flask para la aplicación web

# ============================ 2. Configuración de PRAW ============================
# Reemplaza 'TU_CLIENT_ID' y 'TU_CLIENT_SECRET' con los valores que obtuviste de Reddit.
# El 'user_agent' es un identificador para tu aplicación; usa algo único.
reddit = praw.Reddit(
    client_id="TU_CLIENT_ID",
    client_secret="TU_CLIENT_SECRET",
    user_agent="MiScraperUniversitarioApp/0.1 by u/TuUsuarioDeReddit" # Reemplaza con tu usuario de Reddit
)

# ============================ 3. Inicialización de Flask ============================
app = Flask(__name__)

# ============================ 4. Función para Obtener Comentarios de Reddit ============================
def get_reddit_comments(subreddit_name, keyword, limit=25):
    """
    Busca comentarios en un subreddit dado que contengan una palabra clave.
    Args:
        subreddit_name (str): El nombre del subreddit (ej. "AskReddit").
        keyword (str): La palabra clave a buscar en los posts y comentarios.
        limit (int): El número máximo de comentarios a recolectar.
    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa un comentario.
    """
    comments_data = [] # Lista para almacenar los comentarios encontrados
    try:
        # Intenta obtener el subreddit. Si no existe, praw.Reddit lanzará una excepción.
        subreddit = reddit.subreddit(subreddit_name)

        # Busca "submissions" (posts) dentro del subreddit que contengan la palabra clave.
        # Solo obtenemos un límite de posts para no saturar.
        for submission in subreddit.search(keyword, limit=5): # Buscar en hasta 5 posts relevantes
            # Esto expande "MoreComments" y carga los comentarios de primer nivel.
            submission.comments.replace_more(limit=0)
            # Itera a través de todos los comentarios cargados en esta submission.
            for comment in submission.comments.list():
                # Nos aseguramos de que el objeto sea un comentario real y tenga un cuerpo.
                if hasattr(comment, 'body'):
                    comments_data.append({
                        'author': comment.author.name if comment.author else '[deleted]', # Nombre del autor o '[deleted]'
                        'body': comment.body, # Contenido del comentario
                        'score': comment.score, # Puntuación (karma) del comentario
                        'created_utc': comment.created_utc, # Timestamp de creación (UTC)
                        'permalink': comment.permalink # Enlace directo al comentario
                    })
                    # Si ya hemos alcanzado el límite de comentarios total, salimos.
                    if len(comments_data) >= limit:
                        break
            # Si ya hemos alcanzado el límite de comentarios total, salimos del bucle de submissions.
            if len(comments_data) >= limit:
                break

    except Exception as e:
        # Captura cualquier error que pueda ocurrir (subreddit no encontrado, problemas de conexión, etc.)
        print(f"Error al obtener comentarios: {e}")
        # Puedes retornar una lista vacía o un mensaje de error a la interfaz.
        return []

    return comments_data[:limit] # Aseguramos que no excedamos el límite final.

# ============================ 5. Rutas de la Aplicación Flask ============================

# La ruta principal de la aplicación.
# Acepta solicitudes GET (cuando accedes por primera vez) y POST (cuando envías el formulario).
@app.route('/', methods=['GET', 'POST'])
def index():
    comments = [] # Inicializamos una lista vacía para los comentarios
    error_message = None # Para almacenar mensajes de error

    # Si la solicitud es POST (el usuario envió el formulario)
    if request.method == 'POST':
        # Obtenemos los valores del formulario
        subreddit_name = request.form['subreddit']
        keyword = request.form['keyword']

        # Validar que los campos no estén vacíos
        if not subreddit_name or not keyword:
            error_message = "Por favor, ingresa tanto el subreddit como la palabra clave."
        else:
            # Llamamos a nuestra función para obtener comentarios
            comments = get_reddit_comments(subreddit_name, keyword, limit=50) # Intentar obtener hasta 50 comentarios

            if not comments:
                error_message = f"No se encontraron comentarios para '{keyword}' en r/{subreddit_name} o hubo un problema al conectar con Reddit. Intenta con otros términos o subreddit."

    # Renderizamos la plantilla HTML 'index.html'
    # Le pasamos la lista de comentarios y el mensaje de error para que los muestre.
    return render_template('index.html', comments=comments, error_message=error_message)

# ============================ 6. Ejecutar la Aplicación Flask ============================
# Esto asegura que la aplicación se ejecute solo cuando el archivo es ejecutado directamente.
if __name__ == '__main__':
    # 'debug=True' recarga el servidor automáticamente con cada cambio y muestra errores detallados.
    # ¡Úsalo solo durante el desarrollo, no en producción!
    app.run(debug=True)

```

**Notas Claras sobre `app.py`:**

*   **Librerías:** `praw` es tu puente a Reddit, `Flask` construye la web.
*   **`reddit = praw.Reddit(...)`:** Aquí es donde PRAW se autentica. **¡Recuerda reemplazar los placeholders!**
*   **`app = Flask(__name__)`:** Crea tu aplicación Flask.
*   **`get_reddit_comments(...)`:** Esta es la función central que va a Reddit, busca posts (`submission`) con tu palabra clave y luego extrae los comentarios de esos posts.
    *   `subreddit.search(keyword, limit=5)`: Busca solo en los 5 posts más relevantes para evitar procesar demasiados datos.
    *   `submission.comments.replace_more(limit=0)`: Reddit a menudo esconde comentarios con un enlace "más comentarios". Esta línea le dice a PRAW que los cargue.
    *   `hasattr(comment, 'body')`: Algunos objetos en la lista de comentarios pueden no ser comentarios reales, esto lo filtra.
*   **`@app.route('/', methods=['GET', 'POST'])`:** Esta es una "ruta" de tu aplicación web. Cuando alguien visita `http://127.0.0.1:5000/` (la raíz de tu sitio), esta función `index()` se ejecuta.
    *   `methods=['GET', 'POST']`: Significa que esta ruta puede manejar solicitudes cuando solo visitas la página (`GET`) y cuando envías un formulario (`POST`).
    *   `request.method == 'POST'`: Detecta si el usuario acaba de enviar el formulario.
    *   `request.form['subreddit']`: Obtiene el valor del campo del formulario llamado `subreddit`.
    *   `render_template('index.html', ...)`: Envía los datos (`comments`, `error_message`) a tu archivo HTML para que los muestre.
*   **`if __name__ == '__main__': app.run(debug=True)`:** Inicia el servidor web de Flask. `debug=True` es muy útil para el desarrollo.

---

### **Paso 3: Creación de la Interfaz de Usuario (HTML/CSS)**

Ahora necesitamos crear la página web que el usuario verá. Flask busca las plantillas HTML en una carpeta llamada `templates`.

**Dentro de tu carpeta `reddit_scraper_project`, crea una nueva carpeta llamada `templates`.**
**Dentro de la carpeta `templates`, crea un archivo llamado `index.html`.**

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Comment Scraper</title>
    <style>
        /* ============================ Estilos CSS Básicos ============================ */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 800px;
            margin: 20px auto;
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.2em;
        }

        form {
            background-color: #f7f9fc;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 40px;
            border: 1px solid #e0e6ed;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
            font-size: 1.1em;
        }

        input[type="text"] {
            width: calc(100% - 20px); /* Ajusta el ancho para el padding */
            padding: 12px;
            border: 1px solid #c8d1da;
            border-radius: 6px;
            font-size: 1em;
            box-sizing: border-box; /* Incluye padding y borde en el ancho total */
            transition: border-color 0.3s ease;
        }

        input[type="text"]:focus {
            border-color: #007bff;
            outline: none;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
        }

        button[type="submit"] {
            display: block;
            width: 100%;
            padding: 12px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1.1em;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }

        button[type="submit"]:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
        }

        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #f5c6cb;
            margin-bottom: 25px;
            text-align: center;
            font-weight: bold;
        }

        .results-section {
            margin-top: 50px;
            border-top: 1px solid #e0e6ed;
            padding-top: 30px;
        }

        h2 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.8em;
        }

        .comment-card {
            background-color: #ffffff;
            border: 1px solid #e0e6ed;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease;
        }

        .comment-card:hover {
            transform: translateY(-5px);
        }

        .comment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap; /* Permite que los elementos se envuelvan en pantallas pequeñas */
        }

        .comment-author {
            font-weight: bold;
            color: #007bff;
            font-size: 1.1em;
        }

        .comment-score {
            font-size: 0.95em;
            color: #666;
            background-color: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
        }

        .comment-body {
            font-size: 1em;
            color: #444;
            margin-bottom: 15px;
        }

        .comment-link {
            font-size: 0.9em;
            text-align: right;
        }

        .comment-link a {
            color: #007bff;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .comment-link a:hover {
            color: #0056b3;
            text-decoration: underline;
        }

        /* Estilos responsivos */
        @media (max-width: 600px) {
            .container {
                margin: 10px auto;
                padding: 20px;
                border-radius: 0; /* Sin bordes redondeados en móviles */
                box-shadow: none; /* Sin sombra en móviles */
            }
            h1 {
                font-size: 1.8em;
            }
            input[type="text"] {
                width: 100%;
            }
            .comment-header {
                flex-direction: column;
                align-items: flex-start;
            }
            .comment-score {
                margin-top: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Reddit Comment Scraper</h1>

        <!-- Formulario de Entrada -->
        <form method="POST">
            <div class="form-group">
                <label for="subreddit">Subreddit (ej. AskReddit, programming):</label>
                <input type="text" id="subreddit" name="subreddit" required placeholder="Nombre del subreddit">
            </div>

            <div class="form-group">
                <label for="keyword">Palabra Clave (ej. Python, IA):</label>
                <input type="text" id="keyword" name="keyword" required placeholder="Palabra clave o tema">
            </div>

            <button type="submit">Buscar Comentarios</button>
        </form>

        <!-- Mensajes de Error (si existen) -->
        {% if error_message %}
            <div class="error-message">
                {{ error_message }}
            </div>
        {% endif %}

        <!-- Sección de Resultados (solo se muestra si hay comentarios) -->
        {% if comments %}
            <div class="results-section">
                <h2>Comentarios Encontrados:</h2>
                {% for comment in comments %}
                    <div class="comment-card">
                        <div class="comment-header">
                            <span class="comment-author">u/{{ comment.author }}</span>
                            <span class="comment-score">Score: {{ comment.score }}</span>
                        </div>
                        <p class="comment-body">{{ comment.body }}</p>
                        <p class="comment-link">
                            <a href="https://www.reddit.com{{ comment.permalink }}" target="_blank">Ver en Reddit</a>
                        </p>
                    </div>
                {% endfor %}
            </div>
        {% elif request.method == 'POST' and not error_message %}
            <!-- Este mensaje solo se muestra si el POST se realizó y no hubo comentarios ni errores específicos -->
            <div class="error-message">
                No se encontraron comentarios para tu búsqueda.
            </div>
        {% endif %}
    </div>
</body>
</html>
```

**Notas Claras sobre `index.html`:**

*   **HTML Básico:** Estructura estándar de una página web.
*   **CSS `<style>`:** Estilos básicos para que la página se vea decente. Puedes modificar esto a tu gusto.
*   **`<form method="POST">`:** Este es el formulario que el usuario llenará. El `method="POST"` le dice al navegador que envíe los datos al servidor para que Flask los procese.
*   **`name="subreddit"` y `name="keyword"`:** Estos atributos `name` son cruciales. Flask usa estos nombres (`request.form['subreddit']`) para saber qué datos vienen de qué campo del formulario.
*   **`{% if ... %}` y `{% for ... %}`:** Son parte del motor de plantillas de Flask (Jinja2). Permiten lógica condicional y bucles directamente en tu HTML, usando los datos que le pasaste desde `app.py`.
    *   `{% if error_message %}`: Muestra el bloque de error solo si `error_message` tiene un valor.
    *   `{% for comment in comments %}`: Itera sobre cada comentario en la lista `comments` que Flask le envió, creando una tarjeta (`comment-card`) para cada uno.
    *   `{{ comment.author }}`: Imprime el valor de la clave `author` del diccionario `comment`.
*   **`target="_blank"`:** Abre el enlace del comentario en una nueva pestaña del navegador.

---

### **Paso 4: Ejecutar la Aplicación**

1.  **Guarda Ambos Archivos:** Asegúrate de que `app.py` esté en la raíz de tu carpeta de proyecto y `index.html` esté dentro de `templates/`.

2.  **Activa tu Entorno Virtual (si no lo está):**
    Abre tu terminal, navega a la carpeta de tu proyecto y activa el entorno virtual:
    *   **Windows:** `.\venv\Scripts\activate`
    *   **macOS/Linux:** `source venv/bin/activate`

3.  **Ejecuta la Aplicación Flask:**
    Desde la raíz de tu carpeta de proyecto (donde está `app.py`), ejecuta:
    ```bash
    python app.py
    ```
    Verás un mensaje en tu terminal similar a este:
    ```
     * Serving Flask app 'app'
     * Debug mode: on
     WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
     * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
    ```

4.  **Abre tu Navegador:**
    Copia la dirección `http://127.0.0.1:5000` y pégala en la barra de direcciones de tu navegador.

    ¡Deberías ver tu formulario de búsqueda de Reddit!

---

### **Paso 5: Probar la Aplicación**

1.  **Ingresa un Subreddit y una Palabra Clave:**
    *   **Subreddit:** `AskReddit`
    *   **Palabra Clave:** `AI`
    *   Haz clic en "Buscar Comentarios".

2.  **Ver los Resultados:**
    Si todo funciona correctamente, verás una lista de comentarios relacionados con "AI" de r/AskReddit.

    **Consejos para probar:**
    *   Prueba con subreddits populares como `programming`, `science`, `funny`.
    *   Prueba con palabras clave comunes.
    *   Si no obtienes resultados, prueba con otras combinaciones o verifica si hay algún error en tu terminal (especialmente si no reemplazaste bien tus credenciales de PRAW).

---

¡Felicidades! Has construido una aplicación de web scraping funcional usando Python, Flask y la API de Reddit. Este es un excelente punto de partida para tu proyecto universitario. Puedes expandirlo añadiendo más funcionalidades como guardar comentarios en una base de datos, analizar el sentimiento, o mejorar la interfaz de usuario.

Aquí tienes una imagen que muestra la estructura de carpetas de tu proyecto y cómo se relacionan los archivos `app.py` y `index.html`. 
