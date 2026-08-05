import time
import RPi.GPIO as GPIO

from mfrc522 import SimpleMFRC522
from RPLCD.i2c import CharLCD


ENDERECO_LCD = 0x27
SERVO_PIN = 18

ANGULO_FECHADO = 0
ANGULO_ABERTO = 90

USUARIOS = {
    "665465521850": "Tulio",
    "729854772989": "Daniel"
}


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)


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


def definir_angulo(angulo):
    duty_cycle = 2.5 + (angulo / 18.0)
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.03)


def mover_servo_lentamente(angulo_inicial, angulo_final, atraso=0.04):
    passo = 1 if angulo_final > angulo_inicial else -1

    for angulo in range(angulo_inicial, angulo_final + passo, passo):
        definir_angulo(angulo)
        time.sleep(atraso)

    servo.ChangeDutyCycle(0)


def abrir_cancela():
    mostrar_mensagem("Abrindo", "cancela...")
    mover_servo_lentamente(
        ANGULO_FECHADO,
        ANGULO_ABERTO,
        atraso=0.04
    )


def fechar_cancela():
    mostrar_mensagem("Fechando", "cancela...")
    mover_servo_lentamente(
        ANGULO_ABERTO,
        ANGULO_FECHADO,
        atraso=0.04
    )


try:
    definir_angulo(ANGULO_FECHADO)
    servo.ChangeDutyCycle(0)

    while True:
        mostrar_mensagem("Aproxime a tag", "")

        id_tag, texto = leitor.read()
        id_tag = str(id_tag)

        print(f"Tag lida: {id_tag}")

        if id_tag in USUARIOS:
            nome = USUARIOS[id_tag]

            print(f"Acesso autorizado para {nome}")

            mostrar_mensagem(
                "Bem-vindo,",
                nome
            )

            time.sleep(2)

            abrir_cancela()

            mostrar_mensagem(
                "Cancela aberta",
                "Pode entrar"
            )

            time.sleep(5)

            fechar_cancela()

            mostrar_mensagem(
                "Cancela fechada",
                ""
            )

            time.sleep(2)

        else:
            print("Tag nao cadastrada.")

            mostrar_mensagem(
                "Acesso negado",
                "Tag desconhecida"
            )

            time.sleep(3)

except KeyboardInterrupt:
    print("\nPrograma encerrado.")

finally:
    servo.ChangeDutyCycle(0)
    servo.stop()

    lcd.clear()
    lcd.close(clear=True)

    GPIO.cleanup()
