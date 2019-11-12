from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfSouthAfrica(VdfCore):
    pass

class VdfAttachmentSouthAfrica(VdfAttachment):
    vdf = models.ForeignKey(VdfSouthAfrica)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent