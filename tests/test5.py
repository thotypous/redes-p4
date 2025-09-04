import unittest
import random
from slip import CamadaEnlace

from tests.common import *


class TestPasso5(unittest.TestCase):
    def setUp(self):
        self.next_hop = rand_ip()
        self.linha_serial = LinhaSerial()
        self.enlace = CamadaEnlace({self.next_hop: self.linha_serial})
        self.datagramas = []
        def recebedor(datagrama):
            self.datagramas.append(datagrama)
        def recebedor_erro(datagrama):
            raise Exception("Erro simulado")
        self.recebedor = recebedor
        self.recebedor_erro = recebedor_erro

    def test_recebimento_com_escape_simples_com_erro(self):
        casos = [
            ([b'\xdb\xdd\xc0'], [b'\xdb'], False),
            ([b'\xc0\xdb\xdd\xc0'], [b'\xdb'], False),
            ([b'\xdb\xdd\xc0'], [b'\xdb'], False),
            ([b'\xdb\xdc\xc0'], [b'\xc0'], False),
            ([b'\xc0\xdb\xdc\xc0'], [b'\xc0'], False),
            ([b'\xdb\xdc\xc0'], [b'\xc0'], False),
            ([b'A\xdb\xdd\xc0'], [b'A\xdb'], False),
            ([b'\xc0\xdb\xddB\xc0'], [b'\xdbB'], False),
            ([b'CD\xdb\xdd\xc0'], [b'CD\xdb'], False),
            ([b'EF\xdb\xdcGHI\xc0'], [b'EF\xc0GHI'], False),
            ([b'\xc0JKL\xdb\xdc\xc0'], [b'JKL\xc0'], False),
            ([b'\xdb\xdcMNOP\xc0'], [b'\xc0MNOP'], False),
            ([b'\xc0\xdb\xdd\xc0'], [], True),
            ([b'\xdb\xdd\xc0'], [b'\xdb'], False),
            ([b'\xdb\xdc\xc0'], [], True),
            ([b'\xc0\xdb\xdc\xc0'], [], True),
            ([b'\xdb\xdc\xc0'], [b'\xc0'], False),
            ([b'A\xdb\xdd\xc0'], [], True),
            ([b'\xc0\xdb\xddB\xc0'], [], True),
            ([b'CD\xdb\xdd\xc0'], [b'CD\xdb'], False),
            ([b'EF\xdb\xdcGHI\xc0'], [b'EF\xc0GHI'], False),
            ([b'\xc0JKL\xdb\xdc\xc0'], [b'JKL\xc0'], False),
            ([b'\xdb\xdcMNOP\xc0'], [], True),
        ]
        for entrada, saida, erro in casos:
            with self.subTest(entrada=entrada):
                if erro:
                    self.enlace.registrar_recebedor(self.recebedor_erro)
                else:
                    self.enlace.registrar_recebedor(self.recebedor)
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está limpando o buffer após erro no callback.")
                self.datagramas.clear()

    def test_recebimento_com_escape_quebrado_com_erro(self):
        casos = [
            ([b'\xc0\xdb', b'\xdd\xc0'], [b'\xdb'], False),
            ([b'\xc0', b'\xdb', b'\xdd', b'\xc0'], [b'\xdb'], False),
            ([b'\xc0\xdb', b'\xdc\xc0'], [b'\xc0'], False),
            ([b'\xc0', b'\xdb', b'\xdc', b'\xc0'], [b'\xc0'], False),
            ([b'\xc0A\xdb', b'\xddB\xc0'], [b'A\xdbB'], False),
            ([b'\xc0C', b'D\xdb', b'\xddF', b'\xc0'], [b'CD\xdbF'], False),
            ([b'\xc0G\xdb', b'\xdcHI\xc0'], [], True),
            ([b'\xc0', b'\xdb', b'\xdcJ', b'\xc0'], [b'\xc0J'], False),
        ]
        for entrada, saida, erro in casos:
            with self.subTest(entrada=entrada):
                if erro:
                    self.enlace.registrar_recebedor(self.recebedor_erro)
                else:
                    self.enlace.registrar_recebedor(self.recebedor)
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está limpando o buffer após erro em quadros quebrados.")
                self.datagramas.clear()

    def test_recebimento_multiplos_quadros_com_escape_com_erro(self):
        casos = [
            ([b'ABC\xc0DE\xc0'], [b'ABC', b'DE'], False),
            ([b'\xc0ABC\xc0DE\xc0'], [b'ABC', b'DE'], False),
            ([b'\xc0ABC\xc0\xc0DE\xc0'], [], True),
            ([b'\xc0ABC\xc0\xc0DE\xc0\xc0FGHIJ\xc0'], [b'ABC', b'DE', b'FGHIJ'], False),
        ]
        for entrada, saida, erro in casos:
            with self.subTest(entrada=entrada):
                if erro:
                    self.enlace.registrar_recebedor(self.recebedor_erro)
                else:
                    self.enlace.registrar_recebedor(self.recebedor)
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está limpando o buffer após erro em múltiplos quadros.")
                self.datagramas.clear()

    def test_recebimento_multiplos_quadros_quebrados_com_escape_com_erro(self):
        casos = [
            ([b'A', b'B\xdb\xddC', b'\xc0DE\xc0'], [b'AB\xdbC', b'DE'], False),
            ([b'\xc0AB', b'C\xc0\xdb\xdd', b'DE\xc0'], [b'ABC', b'\xdbDE'], False),
            ([b'\xc0\xdb\xdc', b'ABC', b'\xc0', b'\xc0', b'D', b'E', b'\xc0'], [], True),
            ([b'\xc0', b'ABC\xc0\xc0', b'DE\xc0', b'\xc0F\xdb\xdcGHIJ', b'\xc0'], [b'ABC', b'DE', b'F\xc0GHIJ'], False),
        ]
        for entrada, saida, erro in casos:
            with self.subTest(entrada=entrada):
                if erro:
                    self.enlace.registrar_recebedor(self.recebedor_erro)
                else:
                    self.enlace.registrar_recebedor(self.recebedor)
                for dados in entrada:
                    self.linha_serial.callback(dados)
                self.assertEqual(self.datagramas, saida,
                                 msg=f"Ao receber {entrada!r} pela linha serial, deveriam ter sido reconhecidos os datagramas {saida!r}, mas foram reconhecidos {self.datagramas!r}. Verifique se está limpando o buffer após erro em múltiplos quadros quebrados.")
                self.datagramas.clear()
