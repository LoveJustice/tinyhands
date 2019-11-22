from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfZimbabwe(VdfCore):
    pass

class VdfAttachmentZimbabwe(VdfAttachment):
    vdf = models.ForeignKey(VdfZimbabwe)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent