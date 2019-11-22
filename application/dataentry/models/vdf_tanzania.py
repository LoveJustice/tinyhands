from django.db import models
from .vdf_core import VdfAttachment, VdfCore

class VdfTanzania(VdfCore):
    pass

class VdfAttachmentTanzania(VdfAttachment):
    vdf = models.ForeignKey(VdfTanzania)
    
    def set_parent(self, the_parent):
        self.vdf = the_parent