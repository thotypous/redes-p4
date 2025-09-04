import unittest
import random
from slip import CamadaEnlace

from tests.common import *


class TestPasso1(unittest.TestCase):
    def setUp(self):
        self.next_hop = rand_ip()
        self.linha_serial = LinhaSerial()
        self.enlace = CamadaEnlace({self.next_hop: self.linha_serial})

    def test_delimitacao_quadros(self):
        casos = [
            b'\x01',
            b'\x00\x01',
            b'ABCDEF',
            b'\x10\x20\x30\x40\x50',
            128 * b' ',
            1024 * b' ',
            1500 * b' ',
            b'',  # Datagrama vazio
            b'\xFF',  # Byte especial não relacionado ao SLIP
            b'\x00\xFF\xAA',  # Sequência aleatória
        ]
        for datagrama in casos:
            with self.subTest(datagrama=datagrama):
                self.enlace.enviar(datagrama, self.next_hop)
                esperado = b'\xc0' + datagrama + b'\xc0'
                self.assertEqual(self.linha_serial.fila, esperado,
                                 msg=f"O quadro enviado deveria ser delimitado com bytes 0xC0 no início e fim, mas foi {self.linha_serial.fila!r} em vez de {esperado!r}. Verifique se está adicionando os delimitadores corretamente.")
                self.linha_serial.fila = b''
