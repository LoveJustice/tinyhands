from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfMalawi(VdfCore):
    pass

class VdfAttachmentMalawi(VdfAttachment):
    vdf = models.ForeignKey(VdfMalawi)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent