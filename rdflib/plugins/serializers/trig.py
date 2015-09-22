"""
Trig RDF graph serializer for RDFLib.
See <http://www.w3.org/TR/trig/> for syntax specification.
"""

from collections import defaultdict

from rdflib.plugins.serializers.turtle import TurtleSerializer, _GEN_QNAME_FOR_DT, VERB

from rdflib.term import BNode, Literal

__all__ = ['TrigSerializer']


class TrigSerializer(TurtleSerializer):

    short_name = "trig"
    indentString = 4 * u' '

    def __init__(self, store):
        if store.context_aware:
            self.contexts = list(store.contexts())
            self.default_context = store.default_context.identifier
            if store.default_context:
                self.contexts.append(store.default_context)
        else:
            self.contexts = [store]
            self.default_context = None

        super(TrigSerializer, self).__init__(store)

    def preprocess(self):
        for context in self.contexts:
            self.store = context
            self.getQName(context.identifier)
            self._references = defaultdict(int)
            self._subjects = {}

            for triple in context:
                self.preprocessTriple(triple)

            self._contexts[context]=(self.orderSubjects(), self._subjects, self._references)

    def reset(self):
        super(TrigSerializer, self).reset()
        self._contexts = {}

    def serialize(self, stream, base=None, encoding=None,
                  spacious=None, **args):
        self.reset()
        self.stream = stream
        self.base = base

        if spacious is not None:
            self._spacious = spacious

        self.preprocess()

        self.startDocument()

        for store, (ordered_subjects, subjects, ref) in self._contexts.items():
            self._references = ref
            self._serialized = {}
            self.store = store
            self._subjects = subjects

            print self.default_context, store.identifier
            
            inDefaultGraph=self.default_context is None or store.identifier==self.default_context
            if inDefaultGraph:
                self.depth -= 1
            else:
                if isinstance(store.identifier, BNode):
                    iri = store.identifier.n3()
                else:
                    iri = self.getQName(store.identifier)
                    if iri is None:
                        iri = store.identifier.n3()
                self.write(self.indent() + '\n%s {' % iri)

            self.depth += 1
            for subject in ordered_subjects:
                if self.isDone(subject):
                    continue
                if self.statement(subject):
                    self.write('\n')
            self.depth -= 1
            
            if inDefaultGraph:
                self.depth += 1
                self.write('\n')
            else:
                self.write('}\n')

        self.endDocument()
        stream.write(u"\n".encode('ascii'))
