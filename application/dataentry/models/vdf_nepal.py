from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfNepal(VdfCore):
    pass

class VdfAttachmentNepal(VdfAttachment):
    vdf = models.ForeignKey(VdfNepal)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent