import time
import RPi.GPIO as GPIO

from mfrc522 import SimpleMFRC522
from RPLCD.i2c import CharLCD


ENDERECO_LCD = 0x27

lcd = CharLCD(
    i2c_expander="PCF8574",
    address=ENDERECO_LCD,
    port=1,
    cols=16,
    rows=2,
    charmap="A00",
    auto_linebreaks=False
)

leitor = SimpleMFRC522()


def mostrar_mensagem(linha1="", linha2=""):
    lcd.clear()

    lcd.cursor_pos = (0, 0)
    lcd.write_string(linha1[:16].ljust(16))

    lcd.cursor_pos = (1, 0)
    lcd.write_string(linha2[:16].ljust(16))


try:
    mostrar_mensagem("Leitor RFID", "Aproxime a tag")

    while True:
        id_tag, texto = leitor.read()
        id_tag = str(id_tag)

        print(f"ID da tag: {id_tag}")

        mostrar_mensagem(
            "ID da tag:",
            id_tag
        )

        time.sleep(3)

        mostrar_mensagem(
            "Leitor RFID",
            "Aproxime a tag"
        )

except KeyboardInterrupt:
    print("\nPrograma encerrado.")

finally:
    lcd.clear()
    lcd.close(clear=True)
    GPIO.cleanup()