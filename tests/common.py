import random


class LinhaSerial:
    def __init__(self):
        self.callback = None
        self.fila = b''

    def registrar_recebedor(self, callback):
        self.callback = callback

    def enviar(self, dados):
        self.fila += dados


def rand_ip():
    return '%d.%d.%d.%d' % tuple(random.randint(1, 255) for i in range(4))
