# This needs to lie outside the disassemblylib directory because of Python's arbitrary
# decision to limit relative importing to "packages".

import logging
import struct
import unittest

from disassemblylib import archmips, archm68k, util


class BaseArchTestCase(unittest.TestCase):
    pass


class ArchmipsTestCase(BaseArchTestCase):
    def setUp(self):
        self.arch = archmips.ArchMIPS()
        self.arch.set_operand_type_table(archmips.operand_type_table)
        self.arch.set_instruction_table(archmips.instruction_table)
        
        self.test_data1 = "\x20\x01\x00\x0A"
        self.test_data1_entrypoint = 0x100

    def tearDown(self):
        pass

    def testDisassembly(self):
        # Check that the match gives the expected PC address.
        match, data_idx = self.arch.function_disassemble_one_line(self.test_data1, 0, self.test_data1_entrypoint)
        self.assertEquals(match.pc, self.test_data1_entrypoint + self.arch.constant_pc_offset)
        
        # Check that the match has the expected data words.
        bytes_per_instruction_word = int(self.arch.constant_word_size/8.0)
        data_word = struct.unpack(self.arch.variable_endian_type +"I", self.test_data1[0:bytes_per_instruction_word])[0]
        self.assertListEqual(match.data_words, [ data_word ])

        # Check that the instruction is identified correctly.
        self.assertEquals("ADDI", self.arch.function_get_instruction_string(match, match.vars))
        # Check that the right number of operands are present.
        self.assertEquals(len(match.opcodes), 3)
       
        self.arch.function_get_operand_string(match, match.opcodes[0], match.opcodes[0].vars)
        self.arch.function_get_operand_string(match, match.opcodes[1], match.opcodes[1].vars)
        self.arch.function_get_operand_string(match, match.opcodes[2], match.opcodes[2].vars)

        
class Archm68kTestCase(BaseArchTestCase):
    def setUp(self):
        self.arch = archm68k.ArchM68k()

    def tearDown(self):
        pass

    def testInstructionParsing(self):
        self.arch.set_operand_type_table(archm68k.operand_type_table)
        d = util.process_instruction_list(self.arch, archm68k.instruction_table)
        # print d


class binaryConversionTestCase(unittest.TestCase):
    def testToNumber(self):
        self.assertTrue(util._b2n("1") == 1)
        self.assertTrue(util._b2n("10") == (1<<1))
        self.assertTrue(util._b2n("11") == (1<<1) + 1)
        self.assertTrue(util._b2n("11111111") == 0xFF)
        self.assertTrue(util._b2n("11110000") == 0xF0)
        self.assertTrue(util._b2n("00000000") == 0x00)

    def testFromNumber(self):
        self.assertTrue(util._n2b(1) == "1")
        self.assertTrue(util._n2b(7) == "111")
        self.assertTrue(util._n2b(255) == "11111111")
        self.assertTrue(util._n2b(254) == "11111110")
        self.assertTrue(util._n2b(256) == "100000000")
        
    def testFromNumberPadded(self):
        """ Padded out to multiples of 4 bits (octets). """
        self.assertTrue(util._n2b(1, dynamic_padding=True) == "0001")
        self.assertTrue(util._n2b(15, dynamic_padding=True) == "1111")
        self.assertTrue(util._n2b(16, dynamic_padding=True) == "00010000")
        self.assertTrue(util._n2b(255, dynamic_padding=True) == "11111111")

    def testFromNumberPaddingLength(self):
        self.assertTrue(util._n2b(util._b2n("1"), padded_length=2) == "01")
        self.assertTrue(util._n2b(util._b2n("1"), padded_length=3) == "001")
        for text in ("111", "001", "00001111"):
            value = util._b2n(text)
            self.assertTrue(util._n2b(value, padded_length=len(text)) == text)


if __name__ == "__main__":
    DISPLAY_LOGGING = True

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if DISPLAY_LOGGING:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
    else:
        ch = logging.NullHandler()
    logger.addHandler(ch)
    unittest.main()

