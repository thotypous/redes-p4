import unittest
import random
from slip import CamadaEnlace

from tests.common import *


class TestPasso3(unittest.TestCase):
    def setUp(self):
        self.next_hop = rand_ip()
        self.linha_serial = LinhaSerial()
        self.enlace = CamadaEnlace({self.next_hop: self.linha_serial})
        self.datagramas = []
        def recebedor(datagrama):
            self.datagramas.append(datagrama)
        self.enlace.registrar_recebedor(recebedor)

    def test_recebimento_quadros_simples(self):
        casos = [
            ([b'ABC\xc0'], [b'ABC']),
            ([b'\xc0ABC\xc0'], [b'ABC']),
            ([b'ABC\xc0'], [b'ABC']),
        ]
        for entrada, saida in casos:
            with self.subTest(entrada=entrada):
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está processando quadros simples corretamente.")
                self.datagramas.clear()

    def test_recebimento_quadros_quebrados(self):
        casos = [
            ([b'\xc0ABC', b'\xc0'], [b'ABC']),
            ([b'A', b'BC', b'\xc0'], [b'ABC']),
            ([b'\xc0', b'A', b'BC\xc0'], [b'ABC']),
            ([b'\xc0', b'A', b'BC\xc0'], [b'ABC']),
        ]
        for entrada, saida in casos:
            with self.subTest(entrada=entrada):
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está lidando com quadros quebrados em pedaços.")
                self.datagramas.clear()

    def test_recebimento_multiplos_quadros(self):
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
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está processando múltiplos quadros.")
                self.datagramas.clear()

    def test_recebimento_multiplos_quadros_quebrados(self):
        casos = [
            ([b'A', b'BC', b'\xc0DE\xc0'], [b'ABC', b'DE']),
            ([b'\xc0AB', b'C\xc0', b'DE\xc0'], [b'ABC', b'DE']),
            ([b'\xc0', b'ABC', b'\xc0', b'\xc0', b'D', b'E', b'\xc0'], [b'ABC', b'DE']),
            ([b'\xc0', b'ABC\xc0\xc0', b'DE\xc0', b'\xc0FGHIJ', b'\xc0'], [b'ABC', b'DE', b'FGHIJ']),
        ]
        for entrada, saida in casos:
            with self.subTest(entrada=entrada):
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está lidando com múltiplos quadros quebrados.")
                self.datagramas.clear()

    def test_descarte_datagramas_vazios(self):
        casos = [
            ([b'\xc0\xc0'], []),  # Quadro vazio
            ([b'\xc0ABC\xc0', b'\xc0\xc0'], [b'ABC']),  # Misto com vazio
            ([b'\xc0'], []),  # Quadro incompleto
        ]
        for entrada, saida in casos:
            with self.subTest(entrada=entrada):
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Datagramas vazios ou quadros incompletos devem ser descartados ou ignorados. Recebido: {self.datagramas!r}, esperado: {saida!r}.")
                self.datagramas.clear()
