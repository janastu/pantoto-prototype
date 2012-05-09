from panobj import PanObj
import cPickle

class ViewCategory(PanObj):

    def __init__(self,sessionuser,vcname,perm,persona ):
        PanObj.__init__(self,sessionuser)
        self.name = vcname
        self.permissions = perm
        self.workflowrole = persona # View is associated with a role
        self.id = "vc" + str(self.id)

    def edit(self,perm):
        pass

    def delete():
        pass

    def acl(self,sessionuserid):
        # need not check workflowuser
        if self.workflowrole.hasuser(sessionuserid):
            #print str(self.permissions)
            grpid = ''
            for gid in self.permissions.keys():
                grp = cPickle.load(open(gid+".obj",'rb'))
                if grp.hasuser(sessionuserid):
                    grpid = grp.getid()
                    break
            return self.permissions.getitem(grpid) # Returns a field access set
        else:
            return Null
