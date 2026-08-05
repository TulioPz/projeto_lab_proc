import time
import RPi.GPIO as GPIO

from mfrc522 import SimpleMFRC522
from RPLCD.i2c import CharLCD


ENDERECO_LCD = 0x27

SERVO_PIN = 18
TRIGGER_PIN = 14
ECHO_PIN = 15

ANGULO_FECHADO = 0
ANGULO_ABERTO = 90

DISTANCIA_SEGURA = 20.0
INTERVALO_LEITURA = 0.3

USUARIOS = {
    "729854772989": "Tulio",
    "665465521850": "PSPSPS",
    "347829105638": "Maria"
}


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

GPIO.output(TRIGGER_PIN, GPIO.LOW)

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
        atraso=0.02
    )


def fechar_cancela():
    mostrar_mensagem("Fechando", "cancela...")

    mover_servo_lentamente(
        ANGULO_ABERTO,
        ANGULO_FECHADO,
        atraso=0.04
    )


def medir_distancia():
    GPIO.output(TRIGGER_PIN, GPIO.LOW)
    time.sleep(0.0002)

    GPIO.output(TRIGGER_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, GPIO.LOW)

    inicio_timeout = time.time()

    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        if time.time() - inicio_timeout > 0.03:
            return None

    inicio_pulso = time.time()
    inicio_timeout = time.time()

    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        if time.time() - inicio_timeout > 0.03:
            return None

    fim_pulso = time.time()

    duracao = fim_pulso - inicio_pulso
    distancia = (duracao * 34300) / 2

    return distancia


def aguardar_area_livre():
    mostrar_mensagem(
        "Aguardando",
        "veiculo passar"
    )

    leituras_livres = 0

    while leituras_livres < 3:
        distancia = medir_distancia()

        if distancia is None:
            mostrar_mensagem(
                "Erro no sensor",
                "Cancela aberta"
            )

            print("Falha ao medir a distância.")
            leituras_livres = 0

        else:
            print(f"Distancia: {distancia:.1f} cm")

            if distancia >= DISTANCIA_SEGURA:
                leituras_livres += 1
            else:
                leituras_livres = 0

                mostrar_mensagem(
                    "Veiculo",
                    "detectado"
                )

        time.sleep(INTERVALO_LEITURA)


try:
    definir_angulo(ANGULO_FECHADO)
    servo.ChangeDutyCycle(0)

    time.sleep(1)

    while True:
        mostrar_mensagem(
            "Aproxime a tag",
            ""
        )

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

            time.sleep(1)

            aguardar_area_livre()

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
