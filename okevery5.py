import time
import pyautogui

# ============ CONFIGURACIÓN (edita estas dos líneas con frase y tiempo) ============
frase = "ok"
tiempo = 5 * 60   # segundos entre cada envío (5 minutos = 300)
# ================================================================

ENVIAR_CON_ENTER = True   # True: pulsa Enter después de escribir
CUENTA_ATRAS = 10         # segundos de margen al arrancar para que pinches en el chat

pyautogui.FAILSAFE = True  # mueve el ratón a la esquina superior izquierda para abortar


def escribir_frase(texto):
    # pyautogui.write() falla con tildes y ñ en muchos sistemas,
    # así que se pega desde el portapapeles (más fiable).
    import pyperclip
    pyperclip.copy(texto)
    atajo = "command" if pyautogui.platform.system() == "Darwin" else "ctrl"
    pyautogui.hotkey(atajo, "v")
    time.sleep(0.3)
    if ENVIAR_CON_ENTER:
        pyautogui.press("enter")


def main():
    print(f"Frase : {frase}")
    print(f"Cada  : {tiempo} segundos")
    print(f"Tienes {CUENTA_ATRAS}s para hacer clic en el cuadro de texto del chat...")
    for i in range(CUENTA_ATRAS, 0, -1):
        print(f"  Empieza en {i}...", end="\r")
        time.sleep(1)
    print("\nEn marcha. Ctrl+C en la terminal para parar.\n")

    try:
        while True:
            escribir_frase(frase)
            print(f"[{time.strftime('%H:%M:%S')}] Enviado.")
            time.sleep(tiempo)
    except KeyboardInterrupt:
        print("\nDetenido.")


if __name__ == "__main__":
    main()
