import spacy
from gliner_spacy.pipeline import GlinerSpacy
import libraries.neo4j_lib as nl
from gliner import GLiNER

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("gliner_spacy")

model = GLiNER.from_pretrained("urchade/gliner_mediumv2.1")
