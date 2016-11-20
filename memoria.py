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

    def generarEspacioMemoria(self, tipo, size=1):
        if tipo == 'INT':
            return self.generarMemoriaInt(size)
        if tipo == 'FLOAT':
            return self.generarMemoriaFloat(size)
        if tipo == 'BOOL':
            return self.generarMemoriaBool(size)
        if tipo == 'CHAR':
            return self.generarMemoriaChar(size)
        if tipo == 'STRING':
            return self.generarMemoriaString(size)

    def generarMemoriaInt(self, size=1):
        mem = self.intCount + 1
        self.intCount += size
        return mem + self.INT_MEMORIA

    def generarMemoriaFloat(self, size=1):
        mem = self.floatCount + 1
        self.floatCount +=  size
        return mem + self.FLOAT_MEMORIA

    def generarMemoriaBool(self, size=1):
        mem = self.boolCount + 1
        self.boolCount += size
        return mem + self.BOOL_MEMORIA

    def generarMemoriaChar(self, size=1):
        mem = self.charCount + 1
        self.charCount += size
        return mem + self.CHAR_MEMORIA

    def generarMemoriaString(self, size=1):
        mem = self.stringCount + 1
        self.stringCount += size
        return mem + self.STRING_MEMORIA
