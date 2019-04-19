from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfIndia(VdfCore):
    pass

class VdfAttachmentIndia(VdfAttachment):
    vdf = models.ForeignKey(VdfIndia)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent