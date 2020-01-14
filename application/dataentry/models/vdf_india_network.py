from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfIndiaNetwork(VdfCore):
    pass

class VdfAttachmentIndiaNetwork(VdfAttachment):
    vdf = models.ForeignKey(VdfIndiaNetwork)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent