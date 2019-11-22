from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfKenya(VdfCore):
    pass

class VdfAttachmentKenya(VdfAttachment):
    vdf = models.ForeignKey(VdfKenya)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent