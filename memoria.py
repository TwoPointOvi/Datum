class Memoria:
    def __init__(self, inicio=0):
        self.INT_MEMORIA = inicio + 10000
        self.FLOAT_MEMORIA = inicio + 20000
        self.BOOL_MEMORIA = inicio + 30000
        self.CHAR_MEMORIA = inicio + 40000
        self.STRING_MEMORIA = inicio + 50000

        self.intCount = -1
        self.floatCount = -1
        self.boolCount = -1
        self.charCount = -1
        self.stringCount = -1

    def generarEspacioMemoria(self, tipo):
        if tipo == 'INT':
            return self.generarMemoriaInt()
        if tipo == 'FLOAT':
            return self.generarMemoriaFloat()
        if tipo == 'BOOL':
            return self.generarMemoriaBool()
        if tipo == 'CHAR':
            return self.generarMemoriaChar()
        if tipo == 'STRING':
            return self.generarMemoriaString()

    def generarMemoriaInt(self):
        self.intCount += 1
        return self.intCount + self.INT_MEMORIA

    def generarMemoriaFloat(self):
        self.floatCount += 1
        return self.floatCount + self.FLOAT_MEMORIA

    def generarMemoriaBool(self):
        self.boolCount += 1
        return self.boolCount + self.BOOL_MEMORIA

    def generarMemoriaChar(self):
        self.charCount += 1
        return self.charCount + self.CHAR_MEMORIA

    def generarMemoriaString(self):
        self.stringCount += 1
        return self.stringCount + self.STRING_MEMORIA