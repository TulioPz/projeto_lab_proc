import time
from datetime import datetime

import RPi.GPIO as GPIO

from mfrc522 import SimpleMFRC522
from RPLCD.i2c import CharLCD


ENDERECO_LCD = 0x27

SERVO_PIN = 18
TRIGGER_PIN = 14
ECHO_PIN = 15

LINHAS = [5, 6, 13, 19]
COLUNAS = [26, 21, 20, 16]

TECLAS = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

ANGULO_FECHADO = 0
ANGULO_ABERTO = 90

DISTANCIA_SEGURA = 20.0
INTERVALO_LEITURA = 0.3

HORA_INICIO_SEM_SENHA = 4
HORA_FIM_SEM_SENHA = 20

TENTATIVAS_MAXIMAS = 3
TEMPO_LIMITE_SENHA = 30

USUARIOS = {
    "729854772989": {
        "nome": "Tulio",
        "senha": "1234"
    },
    "665465521850": {
        "nome": "PSPSPS",
        "senha": "5678"
    },
    "347829105638": {
        "nome": "Maria",
        "senha": "4321"
    }
}


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

GPIO.output(TRIGGER_PIN, GPIO.LOW)

for linha in LINHAS:
    GPIO.setup(linha, GPIO.OUT)
    GPIO.output(linha, GPIO.HIGH)

for coluna in COLUNAS:
    GPIO.setup(coluna, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
    mostrar_mensagem(
        "Abrindo",
        "cancela..."
    )

    mover_servo_lentamente(
        ANGULO_FECHADO,
        ANGULO_ABERTO,
        atraso=0.02
    )


def fechar_cancela():
    mostrar_mensagem(
        "Fechando",
        "cancela..."
    )

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

            print("Falha ao medir a distancia.")
            leituras_livres = 0

        else:
            print(f"Distancia: {distancia:.1f} cm")

            if distancia >= DISTANCIA_SEGURA:
                leituras_livres += 1

                mostrar_mensagem(
                    "Area livre",
                    f"Confirmando {leituras_livres}/3"
                )

            else:
                leituras_livres = 0

                mostrar_mensagem(
                    "Veiculo",
                    "detectado"
                )

        time.sleep(INTERVALO_LEITURA)


def horario_exige_senha():
    hora_atual = datetime.now().hour

    return not (
        HORA_INICIO_SEM_SENHA
        <= hora_atual
        < HORA_FIM_SEM_SENHA
    )


def esperar_soltar_tecla(linha, coluna):
    while GPIO.input(COLUNAS[coluna]) == GPIO.LOW:
        time.sleep(0.02)

    GPIO.output(LINHAS[linha], GPIO.HIGH)


def ler_tecla():
    while True:
        for indice_linha, linha in enumerate(LINHAS):
            GPIO.output(linha, GPIO.LOW)

            for indice_coluna, coluna in enumerate(COLUNAS):
                if GPIO.input(coluna) == GPIO.LOW:
                    tecla = TECLAS[indice_linha][indice_coluna]

                    time.sleep(0.05)

                    esperar_soltar_tecla(
                        indice_linha,
                        indice_coluna
                    )

                    return tecla

            GPIO.output(linha, GPIO.HIGH)

        time.sleep(0.01)


def ler_senha_teclado():
    senha_digitada = ""
    inicio = time.time()

    mostrar_mensagem(
        "Digite a senha",
        "# confirma"
    )

    while True:
        if time.time() - inicio > TEMPO_LIMITE_SENHA:
            mostrar_mensagem(
                "Tempo esgotado",
                "Acesso negado"
            )

            time.sleep(2)
            return None

        tecla = ler_tecla()

        if tecla == "#":
            return senha_digitada

        if tecla == "*":
            senha_digitada = ""

        elif tecla.isdigit():
            if len(senha_digitada) < 8:
                senha_digitada += tecla

        mostrar_mensagem(
            "Digite a senha",
            "*" * len(senha_digitada)
        )


def autenticar_com_senha(usuario):
    for tentativa in range(1, TENTATIVAS_MAXIMAS + 1):
        mostrar_mensagem(
            "Horario noturno",
            "Senha obrigatoria"
        )

        time.sleep(2)

        senha_digitada = ler_senha_teclado()

        if senha_digitada is None:
            return False

        if senha_digitada == usuario["senha"]:
            return True

        tentativas_restantes = TENTATIVAS_MAXIMAS - tentativa

        mostrar_mensagem(
            "Senha incorreta",
            f"Restam: {tentativas_restantes}"
        )

        print(
            f"Senha incorreta. "
            f"Tentativas restantes: {tentativas_restantes}"
        )

        time.sleep(2)

    mostrar_mensagem(
        "Acesso bloqueado",
        "Muitas tentativas"
    )

    time.sleep(3)
    return False


def processar_entrada(usuario):
    nome = usuario["nome"]

    mostrar_mensagem(
        "Bem-vindo,",
        nome
    )

    print(f"Acesso autorizado para {nome}")

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

        hora_atual = datetime.now()

        print(f"Tag lida: {id_tag}")
        print(
            "Horario atual:",
            hora_atual.strftime("%H:%M:%S")
        )

        if id_tag not in USUARIOS:
            print("Tag nao cadastrada.")

            mostrar_mensagem(
                "Acesso negado",
                "Tag desconhecida"
            )

            time.sleep(3)
            continue

        usuario = USUARIOS[id_tag]

        if horario_exige_senha():
            print("Horario noturno: senha obrigatoria.")

            senha_correta = autenticar_com_senha(usuario)

            if not senha_correta:
                continue

            print("Senha correta.")

        else:
            print("Horario permitido: acesso somente com RFID.")

        processar_entrada(usuario)

except KeyboardInterrupt:
    print("\nPrograma encerrado.")

finally:
    servo.ChangeDutyCycle(0)
    servo.stop()

    lcd.clear()
    lcd.close(clear=True)

    GPIO.cleanup()