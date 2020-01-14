from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfRwanda(VdfCore):
    pass

class VdfAttachmentRwanda(VdfAttachment):
    vdf = models.ForeignKey(VdfRwanda)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent