from munge.proc.trace import Filter
from munge.trees.traverse import leaves

class DumpTokens(Filter):
    def __init__(self, outfile):
        if isinstance(outfile, basestring):
            self.outfile = outfile
            self.f = file(self.outfile, 'w')
        elif isinstance(outfile, file):
            self.f = outfile
            self.outfile = outfile.name
        else:
            raise FilterException, "Expected filename or file object."
    
    def accept_derivation(self, deriv):
        print >>self.f, "%s|%s" % (deriv.label(), ' '.join(deriv.derivation.text()))
        
import sys
class Tokens(DumpTokens, Filter):
    def __init__(self):
        DumpTokens.__init__(self, sys.stdout)
        
    opt = "-t"
    long_opt = "--tokens"