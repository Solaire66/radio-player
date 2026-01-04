import tkinter as tk
from tkinter import messagebox
import vlc  # Asegúrate de que 'python-vlc' esté instalado (pip install python-vlc)
import threading
import time  # Aunque no se usa directamente en la lógica VLC, lo dejaremos si es necesario más adelante

# --- Configuraciones ---
# Es crucial que estas URLs sean flujos de audio DIRECTOS.
# Las URLs de APIs de streaming a menudo no funcionan directamente.
STATIONS = {
    "Radio Nuages (Monterrey, MX)": "https://pureplay.cdnstream1.com/6016_64.aac",
    "La Lupe 105.3 ": "https://us-b7-i-e-fn1-audio.cdn.mdstrm.com/live-audio-aw/6737993c9422ca09f9b9ea70?aid=579bd29dc99290cf08362c3b&property=radio-garden&pid=nZWv6kTNxPlPCYsrNYhb5V13kc8emJzf&sid=MbLISe3YjfUkjAu7Jda80tPVEKJR2J9V&uid=yTs0H9mUkpXfmJyfDpCY5dn5lNA3NJyL&es=us-b7-i-e-fn1-audio.cdn.mdstrm.com&ote=1767392712264&ot=XkUClrv6wMw74_MEnT6E8A&proto=https&pz=us&cP=128000&awCollectionId=579bd29dc99290cf08362c3b&aw_0_1st.playerId=radio-garden&liveId=6737993c9422ca09f9b9ea70&referer=https%3A%2F%2Fradio.garden%2F&propertyName=radio-garden&propertyType=rss-app&listenerId=yTs0H9mUkpXfmJyfDpCY5dn5lNA3NJyL",
    "Banda 93.3": "https://14553.live.streamtheworld.com/XHQQ_FMAAC.aac",  # Ejemplo de URL que funciona con VLC
    "Classic 106.9": "https://us-b7-i-e-fn1-audio.cdn.mdstrm.com/live-audio-aw/673788019b826f0dc1842750?aid=579bd29dc99290cf08362c3b&property=radio-garden&pid=QmbnCjJ8DG3K2XaQwu6JxvVxgNxOvBrm&sid=MbLISe3YjfUkjAu7Jda80tPVEKJR2J9V&uid=yTs0H9mUkpXfmJyfDpCY5dn5lNA3NJyL&es=us-b7-i-e-fn1-audio.cdn.mdstrm.com&ote=1767392551838&ot=MovNSxJ3_qbcUHFoBvB7Wg&proto=https&pz=us&cP=128000&awCollectionId=579bd29dc99290cf08362c3b&aw_0_1st.playerId=radio-garden&liveId=673788019b826f0dc1842750&referer=https%3A%2F%2Fradio.garden%2F&propertyName=radio-garden&propertyType=rss-app&listenerId=yTs0H9mUkpXfmJyfDpCY5dn5lNA3NJyL",
    # Ejemplo m3u8
}

# --- Variables Globales ---
# ES ABSOLUTAMENTE CRUCIAL que esta variable se inicialice a None AQUÍ
# para que exista en el ámbito global desde el principio.
current_player = None
is_playing = False  # Indica si se está intentando reproducir algo
metadata_update_id = None

# --- Funciones de Reproducción ---

def play_station_vlc(url):
    """
    Función que maneja la reproducción de la estación de radio
    utilizando la librería VLC. Esta función se ejecuta en un hilo
    separado para no bloquear la interfaz de usuario.
    """
    global current_player, is_playing # noqa: F824
    try:
        # Asegurarse de que no haya un reproductor activo antes de crear uno nuevo.
        # Esto es más bien una doble verificación, ya que select_and_play() ya llama a stop_playing().
        if current_player:
            current_player.stop()
            current_player = None

        # Crea una instancia de VLC.
        # '--no-xlib' puede ser útil en algunos entornos Linux sin interfaz gráfica.
        # '--quiet' reduce la verbosidad de los mensajes de VLC.
        instance = vlc.Instance('--no-xlib', '--quiet')

        # Crea un objeto media a partir de la URL del flujo de audio.
        media = instance.media_new(url)

        # Crea un objeto reproductor para controlar la reproducción.
        current_player = instance.media_player_new()

        # Asigna el objeto media al reproductor.
        current_player.set_media(media)

        # Inicia la reproducción.
        current_player.play()
        is_playing = True
        status_label.config(text=f"Reproduciendo: {selected_station.get()}")

        # Opcional: monitorear el estado del reproductor en un bucle o evento para UI más dinámica
        # Por ahora, solo iniciamos y asumimos que está reproduciendo.
        # VLC maneja el streaming internamente.

    except Exception as e:
        # Captura cualquier error durante la inicialización o reproducción de VLC.
        messagebox.showerror("Error de reproducción",
                            f"No se pudo reproducir la estación. Asegúrate de que la URL sea válida y VLC esté instalado.\nError: {e}")
        is_playing = False
        status_label.config(text="Detenido")
        current_player = None  # Asegurarse de limpiar el reproductor en caso de error


def select_and_play():
    """
    Función llamada al presionar el botón "Reproducir".
    Detiene cualquier reproducción existente y luego inicia una nueva
    en un hilo separado para mantener la interfaz de usuario responsiva.
    """
    global current_player, is_playing # noqa: F824
    selected_name = selected_station.get()
    url = STATIONS.get(selected_name)

    if not url:
        # Muestra una advertencia si no se seleccionó ninguna estación válida.
        messagebox.showwarning("Selección", "Por favor, selecciona una estación de la lista.")
        return

    # Detener la reproducción actual si hay alguna activa.
    # Esta llamada es segura porque 'current_player' se inicializa a 'None'
    # o se establece a 'None' después de detener una reproducción.
    stop_playing()

    # Iniciar la nueva reproducción en un hilo separado.
    # El uso de un hilo evita que la interfaz gráfica se congele mientras VLC carga y reproduce.
    play_thread = threading.Thread(target=play_station_vlc, args=(url,))
    play_thread.daemon = True  # Hace que el hilo se detenga cuando el programa principal (Tkinter) se cierra.
    play_thread.start()


def stop_playing():
    """
    Intenta detener la reproducción actual de la estación de radio.
    """
    global current_player, is_playing # noqa: F824
    if current_player:  # <--- SOLO ENTRA AQUÍ SI HAY UN REPRODUCTOR ACTIVO
        # Si existe un objeto reproductor de VLC, se detiene la reproducción.
        current_player.stop()
        current_player = None  # Limpia la referencia al reproductor para futuras reproducciones
        is_playing = False
        status_label.config(text="Detenido")
        # Este messagebox.showinfo() ahora solo se mostrará si el usuario presiona el botón "Detener"
        # y había algo reproduciéndose.
        # messagebox.showinfo("Detener", "Reproducción detenida.")
    # El bloque 'else' ha sido eliminado para evitar el mensaje prematuro.


# --- Configuración de la Interfaz Gráfica (Tkinter) ---

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sintonizador de Radio Simple")
    root = tk.Tk()
    root.title("Sintonizador de Radio Simple")
    root.geometry("400x300")
    root.resizable(False, False)  # Evita que la ventana se pueda redimensionar

    # Etiqueta de título
    title_label = tk.Label(root, text="Selecciona una Estación:", font=("Helvetica", 14, "bold"))
    title_label.pack(pady=10)

    # Dropdown para seleccionar estaciones
    station_names = list(STATIONS.keys())
    selected_station = tk.StringVar(root)
    # Establece el valor inicial del dropdown. Si no hay estaciones, muestra un mensaje.
    selected_station.set(station_names[0] if station_names else "No hay estaciones")

    station_menu = tk.OptionMenu(root, selected_station, *station_names)
    station_menu.config(width=40, font=("Helvetica", 10))
    station_menu.pack(pady=5)

    # Botón Reproducir
    play_button = tk.Button(root, text="Reproducir", command=select_and_play, font=("Helvetica", 12), bg="#4CAF50",
                            fg="white")
    play_button.pack(pady=10)

    # Botón Detener
    stop_button = tk.Button(root, text="Detener", command=stop_playing, font=("Helvetica", 12), bg="#f44336", fg="white")
    stop_button.pack(pady=5)

    # Etiqueta de estado
    status_label = tk.Label(root, text="Detenido", font=("Helvetica", 10), fg="blue")
    status_label.pack(pady=10)

    # Iniciar el bucle principal de Tkinter.
    # Esto mantiene la ventana abierta y procesa los eventos de la UI.
    root.mainloop()

