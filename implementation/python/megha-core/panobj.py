from utilities import History, User, Role, Permissions, Session
from datetime import datetime



class PanObj:
    '''PanObj is to be inherited by all Pantoto Classes.
      Its the Object that captures generalizations over
      the evolution of Pantoto
    '''
    uid_counter = 0

    def __init__(self, sessionuserid):
        self.__class__.uid_counter += 1
        self.id = self.__class__.uid_counter
        self.history = History(self.id,sessionuserid,0) # how to initialise?
     
     #self.permissions = Permissions()
        self.authors = [sessionuserid,]

    def __str__(self):
        printstr = "\nPanObj ID:" + self.id
        printstr += "\nHistory:" + self.history
        printstr += "\nPermissions:" + self.permissions
        printstr += "\nAuthor:" + self.authors
        print printstr

    def getid(self):
        return self.id
