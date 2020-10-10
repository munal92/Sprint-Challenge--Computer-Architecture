"""CPU functionality."""

import sys
# The MAR contains the address that is being read or written to
# The MDR contains the data that was read or the data to write.
# R5 is reserved as the interrupt mask (IM)
# R6 is reserved as the interrupt status (IS)
# R7 is reserved as the stack pointer (SP)
# PC: Program Counter, address of the currently executing instruction
# IR: Instruction Register, contains a copy of the currently executing instruction
# MAR: Memory Address Register, holds the memory address we're reading or writing
# MDR: Memory Data Register, holds the value to write or the value just read
# FL: Flags, see below
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[7] = 0xFF
        self.SP = 7  # stack pointer
        self.flags = {'L': 0, 'G': 0, 'E': 0}  # flags

    def load(self, filename):

        address = 0
        with open(filename) as fp:
            for line in fp:
                comment_split = line.split("#")
                num = comment_split[0].strip()
                if num == '':
                    continue
                val = int(num, 2)
                self.ram_write(address, val)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == 'CMP':
            if reg_a == reg_b:
                self.flags = {'L': 0, 'G': 0, 'E': 1}
            elif reg_a < reg_b:
                self.flags = {'L': 1, 'G': 0, 'E': 0}
            elif reg_a > reg_b:
                self.flags = {'L': 0, 'G': 1, 'E': 0}

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            # self.trace()
            inst_register = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            if inst_register == LDI:
                # print(
                #     f'operand 1:{operand_a} \n operand 2: {operand_b} , res hex (8): {0b00001000}')
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif inst_register == PRN:
                value_to_print = self.reg[operand_a]
                print(f'PRN -> {value_to_print}')
                self.pc += 2

            elif inst_register == HLT:
                self.running = False

            elif inst_register == MUL:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
                self.pc += 3

            elif inst_register == PUSH:
                self.reg[self.SP] -= 1  # Decrement to SP to push the value
                registerToValueIn = operand_a
                valueInThisRegister = self.reg[registerToValueIn]
                self.ram_write(self.reg[self.SP], valueInThisRegister)
                self.pc += 2

            elif inst_register == POP:
                topValueInStack = self.ram_read(self.reg[self.SP])
                self.reg[operand_a] = topValueInStack
                self.reg[self.SP] += 1
                self.pc += 2

            elif inst_register == CALL:
                self.reg[self.SP] -= 1
                addressOfNextCommand = self.pc + 2
                self.ram_write(self.reg[self.SP], addressOfNextCommand)
                addressToJumpTo = self.reg[operand_a]
                self.pc = addressToJumpTo

            elif inst_register == RET:
                addressToReturnTo = self.ram_read(self.reg[self.SP])
                self.ram_write(self.reg[self.SP], self.reg[self.SP]+1)
                self.pc = addressToReturnTo

            elif inst_register == ADD:
                self.reg[operand_a] = self.reg[operand_a] + self.reg[operand_b]
                self.pc += 3

            elif inst_register == JMP:
                self.pc = self.reg[operand_a]

            elif inst_register == JEQ:
                if self.flags['E'] == 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            elif inst_register == JNE:
                if self.flags['E'] == 0:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            elif inst_register == CMP:
                self.alu('CMP', self.reg[operand_a], self.reg[operand_b])
                self.pc += 3
            else:
                sys.exit(1)

        # self.print_reg()

    def ram_read(self, register_address):

        return self.ram[register_address]

    def ram_write(self, register_address, value_to_write):
        self.ram[register_address] = value_to_write
        return self.ram_read(register_address)

    def print_reg(self):
        print(f'{self.reg}')
