from panobj import PanObj
from field import Field
from utilities import *
import cPickle
import copy

class Pagelet(PanObj):

    def __init__(self,sessionuser, vcs = None, fs = None):
        PanObj.__init__(self,sessionuser)
        self.status = "draft" # need to define flag :{draft,published}
        # History, Date, Author and Permissions lie within PanObj
        # A pagelets initialisation is independent of views and fields
        # self.views = vcs #views : ViewCategory set
        self.views = vcs
        # pagelets can have fields that are not necessarily associated 
        # with a view.
        # self.fields = [(f, Null) for f in self.views.fields] #FieldData set
        self.fields = fs
        # Reworking the ID
        self.id = "p"+str(self.id)
        # Maintaining reference of all pagelets posted similar from this draft pagelet.
        # similars?
        self.leaves =[]

    def attachcategory(self,viewcategory):
        '''
        Attach a ViewCategory to a pagelet
        This should make sure that workflow consistencies are respected
        For now, ViewCategory.purpose is the workflow label
        '''
        # Need to understand what is meant by purpose , here
        # Maybe a need for approval by workflow admin, etc
        # if attachable(self.views, c.purpose): #X[ ]X
        self.views.append(viewcategory)
        for eachp in self.leaves:
            p = cPickle.load(open(eachp + ".obj",'rb'))
            p.views.append(viewcategory)
        # return c #yeild fields, populate.
        # else:
        # return Null #fail, cannot attach.

    def extendpagelet(self,field):
        '''
        This method would allow extending the pagelet by adding new fields
        '''
        self.fields.append(field)
        # check: can extending violate workflow intention consistency


    def acl(self,sessionuserid):  # session.u: Persona -> FieldAccess set
        '''
        Which fields of the pagelet can a user.persona access
        depends on the permissions set at various ViewCategory
        that this pagelet is attached to ie., self.views
        '''
        myacl = {}
        permissions = Permissions()
        for view in self.views:  #views.acl(session.u)
            permissions.merge(view.acl(sessionuserid))
        # Move from label permissioning to ID permissioning. Need to see how this will get implemented later
        # Any cange of permissioning may want to get refelected on all copies of a field
        # just like any change in the views to a pagelet must get refelected on all its leaves 

        for f in self.fields:  #all my fields, no permissions
            myacl[f.getid()] = permissions.getitem(f.getlabel())
        return myacl


    def view(self,sessionuserid):
        '''
        For fields in cs, show readable fields
        '''
        fieldset = self.acl(sessionuserid)
        #get field's by ID, retrieve the value associated and return
        #here's where persistence will come into play first
        print "\nPagelet Field Access list" 
        print fieldset
        print "\nPagelet View"
        for field in fieldset.keys():
            fld = cPickle.load(open(field + ".obj",'rb'))
            if 'r' in list(fieldset[field]) or (fieldset[field] =='-w' and self.isauthor(sessionuserid)==True): 
                print "\n" + fld.getlabel() + "=" + fld.getvalue()
        

    def edit(self,sessionuserid):
        '''
        For fields in cs, show editable fields
        '''
        fieldset = self.acl(sessionuserid)
        for field in fieldset.keys():
            if 'w' not in list(fieldset[field]):
                del fieldset[field]
        return fieldset
                
                
    def publish(self):
        self.status = "published"

    def delete(self):
        '''
        Delete can be tricky. 
        Who has to right to delete if it "belongs" to various personas
        Need to revisit later.
        '''
        pass

    def postsimilar(self,sessionuserid):
        newf = []
        for fld in self.fields:
            f = Field(sessionuserid,fld.decoration,fld.label)
            newf.append(f)
            cPickle.dump(f, open(f.getid()+".obj",'wb'))
        newp = Pagelet(sessionuserid,self.views,newf)
        self.leaves.append(newp.getid())
        cPickle.dump(self, open(self.getid()+".obj",'wb'))
        cPickle.dump(self, open(newp.getid()+".obj",'wb'))
        return newp
        #p... = ...  start cloning


    def listpagelets(self,sessionuserid,pgts):
        # To simulate the query of a database , just adding known pagelet ids into a tuple
        print "\nPagelet List"
        printstr =""
        newrow = {}
        colhead =[]
        for pgt in pgts:
            fieldset = pgt.acl(sessionuserid)
            newdict ={}
            for field in fieldset.keys():
                if 'r' in list(fieldset[field]) or (fieldset[field] =='-w' and pgt.isauthor(sessionuserid)==True): 
                    fld = cPickle.load(open(field + ".obj",'rb'))
                    newdict[fld.getlabel()] = fld.getvalue()
                    if fld.getlabel() not in colhead:
                        colhead.append(fld.getlabel())
            newrow[pgt.getid()] = newdict 
        printstr += "   "
        for eachcol in colhead:
            printstr += eachcol + "  "
        printstr += "\n"
        for eachp in newrow.keys():
            printstr += eachp + "  "
            p = newrow[eachp]
            for eachcol in colhead:
                if eachcol in p.keys():
                    printstr += str(p[eachcol]) + "  "
            printstr += "\n"
        print printstr

    def isauthor(self,sessionuserid):
        if sessionuserid in self.authors:
            return True
        else:
            return False
