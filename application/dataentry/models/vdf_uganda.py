from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfUganda(VdfCore):
    pass

class VdfAttachmentUganda(VdfAttachment):
    vdf = models.ForeignKey(VdfUganda)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent