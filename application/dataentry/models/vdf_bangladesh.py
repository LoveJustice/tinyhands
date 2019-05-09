from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfBangladesh(VdfCore):
    pass

class VdfAttachmentBangladesh(VdfAttachment):
    vdf = models.ForeignKey(VdfBangladesh)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent