import unittest
import random
from slip import CamadaEnlace

from tests.common import *


class TestPasso2(unittest.TestCase):
    def setUp(self):
        self.next_hop = rand_ip()
        self.linha_serial = LinhaSerial()
        self.enlace = CamadaEnlace({self.next_hop: self.linha_serial})

    def test_escape_sequencias(self):
        casos = [
            (b'\xc0', b'\xdb\xdc'),
            (b'A\xc0', b'A\xdb\xdc'),
            (b'\xc0B', b'\xdb\xdcB'),
            (b'C\xc0D', b'C\xdb\xdcD'),
            (b'\xdb', b'\xdb\xdd'),
            (b'$\xdb', b'$\xdb\xdd'),
            (b'\xdba', b'\xdb\xdda'),
            (b'T\xdbk', b'T\xdb\xddk'),
            (b'\xdb\xc0', b'\xdb\xdd\xdb\xdc'),
            (b'\xc0\xdb', b'\xdb\xdc\xdb\xdd'),
            (b'3K@\xdb4lK\xc0lM', b'3K@\xdb\xdd4lK\xdb\xdclM'),
            (b'L1\xc0llk\xdba', b'L1\xdb\xdcllk\xdb\xdda'),
            (b'\xdb\xdc', b'\xdb\xdd\xdc'),  # Combinação recursiva: \xdb vira \xdb\xdd, então \xdb\xdc vira \xdb\xdd\xdc
            (b'\xdb\xdd', b'\xdb\xdd\xdd'),  # Escape recursivo: \xdb vira \xdb\xdd, então \xdb\xdd vira \xdb\xdd\xdd
        ]
        for datagrama, esperado_meio in casos:
            with self.subTest(datagrama=datagrama):
                self.enlace.enviar(datagrama, self.next_hop)
                fila = self.linha_serial.fila
                self.assertTrue(fila.startswith(b'\xc0'),
                                msg=f"O quadro deve começar com byte 0xC0, mas começou com {fila[:1]!r}. Adicione o delimitador de início.")
                self.assertTrue(fila.endswith(b'\xc0'),
                                msg=f"O quadro deve terminar com byte 0xC0, mas terminou com {fila[-1:]!r}. Adicione o delimitador de fim.")
                meio = fila[1:-1]
                self.assertEqual(meio, esperado_meio,
                                 msg=f"O datagrama {datagrama!r} deveria ter sido transformado em {esperado_meio!r} com sequências de escape, mas foi transformado em {meio!r}. Verifique as substituições de 0xC0 e 0xDB.")
                self.linha_serial.fila = b''
