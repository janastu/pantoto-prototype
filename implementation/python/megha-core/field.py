from panobj import PanObj

class Field(PanObj):

    def __init__(self, sessionuser, deco, label, val = None):
        PanObj.__init__(self,sessionuser)
        self.decoration = deco
        self.label = label
        self.value = val
        self.id = "f" + str(self.id)
        

    def setvalue(self, val):
        self.value = val

    def getvalue(self):
        return self.value

    def getlabel(self):
        return self.label
