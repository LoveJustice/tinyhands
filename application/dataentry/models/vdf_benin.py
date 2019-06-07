from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfBenin(VdfCore):
    pass

class VdfAttachmentBenin(VdfAttachment):
    vdf = models.ForeignKey(VdfBenin)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent