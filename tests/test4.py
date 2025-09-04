import unittest
import random
from slip import CamadaEnlace

from tests.common import *


class TestPasso4(unittest.TestCase):
    def setUp(self):
        self.next_hop = rand_ip()
        self.linha_serial = LinhaSerial()
        self.enlace = CamadaEnlace({self.next_hop: self.linha_serial})
        self.datagramas = []
        def recebedor(datagrama):
            self.datagramas.append(datagrama)
        self.enlace.registrar_recebedor(recebedor)

    def test_recebimento_com_escape_simples(self):
        casos = [
            ([b'\xdb\xdd\xc0'], [b'\xdb']),
            ([b'\xc0\xdb\xdd\xc0'], [b'\xdb']),
            ([b'\xdb\xdd\xc0'], [b'\xdb']),
            ([b'\xdb\xdc\xc0'], [b'\xc0']),
            ([b'\xc0\xdb\xdc\xc0'], [b'\xc0']),
            ([b'\xdb\xdc\xc0'], [b'\xc0']),
            ([b'A\xdb\xdd\xc0'], [b'A\xdb']),
            ([b'\xc0\xdb\xddB\xc0'], [b'\xdbB']),
            ([b'CD\xdb\xdd\xc0'], [b'CD\xdb']),
            ([b'EF\xdb\xdcGHI\xc0'], [b'EF\xc0GHI']),
            ([b'\xc0JKL\xdb\xdc\xc0'], [b'JKL\xc0']),
            ([b'\xdb\xdcMNOP\xc0'], [b'\xc0MNOP']),
            ([b'\xdb'], []),  # Escape incompleto
            ([b'\xdb\xFF'], []),  # Sequência inválida
        ]
        for entrada, saida in casos:
            with self.subTest(entrada=entrada):
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está processando sequências de escape corretamente.")
                self.datagramas.clear()

    def test_recebimento_com_escape_quebrado(self):
        casos = [
            ([b'\xc0\xdb', b'\xdd\xc0'], [b'\xdb']),
            ([b'\xc0', b'\xdb', b'\xdd', b'\xc0'], [b'\xdb']),
            ([b'\xc0\xdb', b'\xdc\xc0'], [b'\xc0']),
            ([b'\xc0', b'\xdb', b'\xdc', b'\xc0'], [b'\xc0']),
            ([b'\xc0A\xdb', b'\xddB\xc0'], [b'A\xdbB']),
            ([b'\xc0C', b'D\xdb', b'\xddF', b'\xc0'], [b'CD\xdbF']),
            ([b'\xc0G\xdb', b'\xdcHI\xc0'], [b'G\xc0HI']),
            ([b'\xc0', b'\xdb', b'\xdcJ', b'\xc0'], [b'\xc0J']),
        ]
        for entrada, saida in casos:
            with self.subTest(entrada=entrada):
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está lidando com sequências de escape em quadros quebrados.")
                self.datagramas.clear()

    def test_recebimento_multiplos_quadros_com_escape(self):
        casos = [
            ([b'ABC\xc0DE\xc0'], [b'ABC', b'DE']),
            ([b'\xc0ABC\xc0DE\xc0'], [b'ABC', b'DE']),
            ([b'\xc0ABC\xc0\xc0DE\xc0'], [b'ABC', b'DE']),
            ([b'\xc0ABC\xc0\xc0DE\xc0\xc0FGHIJ\xc0'], [b'ABC', b'DE', b'FGHIJ']),
        ]
        for entrada, saida in casos:
            with self.subTest(entrada=entrada):
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está processando múltiplos quadros com escape.")
                self.datagramas.clear()

    def test_recebimento_multiplos_quadros_quebrados_com_escape(self):
        casos = [
            ([b'A', b'B\xdb\xddC', b'\xc0DE\xc0'], [b'AB\xdbC', b'DE']),
            ([b'\xc0AB', b'C\xc0\xdb\xdd', b'DE\xc0'], [b'ABC', b'\xdbDE']),
            ([b'\xc0\xdb\xdc', b'ABC', b'\xc0', b'\xc0', b'D', b'E', b'\xc0'], [b'\xc0ABC', b'DE']),
            ([b'\xc0', b'ABC\xc0\xc0', b'DE\xc0', b'\xc0F\xdb\xdcGHIJ', b'\xc0'], [b'ABC', b'DE', b'F\xc0GHIJ']),
        ]
        for entrada, saida in casos:
            with self.subTest(entrada=entrada):
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está lidando com múltiplos quadros quebrados com escape.")
                self.datagramas.clear()
