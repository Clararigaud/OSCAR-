class world(list):
    def __init__(self,*args, **kwargs):
        list.__init__(self,*args, **kwargs)
        #self.__0__ = 1
        
class place(object):
    def __init__(self):
        self.agent = None
        
    @property
    def occupied(self):
        pass
        
    
