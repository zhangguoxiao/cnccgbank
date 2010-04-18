from __future__ import with_statement
from munge.proc.filter import Filter
import os, re

class OutputDerivation(object):
    '''Writes out a derivation to disk.'''
    def __init__(self, transformer=None, fn_template=None, outdir_template=None):
        '''Where _transformer_ is a function which receives each derivation bundle and
returns the string to write, and _fn_template_ is a format string with two format
arguments (the section and document #), creates an OutputDerivation.'''
        self.transformer = transformer or (lambda x: x.derivation)
        self.outdir_template = outdir_template or (lambda outdir, _: outdir)
        self.fn_template = fn_template or (lambda bundle: "chtb_%02d%02d.fid" % (bundle.sec_no, bundle.doc_no))
        
    def write_derivation(self, bundle):
        outdir_path = self.outdir_template(self.outdir, bundle)

        if not os.path.exists(outdir_path): os.makedirs(outdir_path)
        output_filename = os.path.join(outdir_path, self.fn_template(bundle))

        with file(output_filename, 'a') as f:
            print >>f, self.transformer(bundle)

class OutputPrefacedPTBDerivation(OutputDerivation):
    '''Writes out PTB nodes one to a line, each preceded by a preface line with that
node's document ID.'''
    def __init__(self):
        def fix_label(label):
            matches = re.match(r'(\d+):(\d+)\((\d+)\)', label)
            
            if matches and len(matches.groups()) == 3:
                sec, doc, deriv = map(int, matches.groups())
                return "wsj_%02d%02d.%d" % (sec, doc, deriv)
            raise Exception, "Invalid label %s" % label

        def make_header(bundle):
            return 'ID=%s PARSER=GOLD NUMPARSE=1' % fix_label(bundle.label())
            
        def printer(bundle):
            return '\n'.join((
                make_header(bundle),
                repr(bundle.derivation)))

        OutputDerivation.__init__(self, printer)

class OutputCCGbankDerivation(OutputDerivation):
    '''Writes out CCGbank nodes in the CCGbank format.'''
    def __init__(self):
        def fix_label(label):
            matches = re.match(r'(\d+):(\d+)\((\d+)\)', label)
            
            if matches and len(matches.groups()) == 3:
                sec, doc, deriv = map(int, matches.groups())
                return "wsj_%02d%02d.%d" % (sec, doc, deriv)
            raise Exception, "Invalid label %s" % label
                
        def make_header(bundle):
            return 'ID=%s PARSER=GOLD NUMPARSE=1' % fix_label(bundle.label())
            
        def printer(bundle):
            return '\n'.join((
                make_header(bundle), 
                bundle.derivation.ccgbank_repr()))

        OutputDerivation.__init__(self, printer, outdir_template=lambda dir, bundle: "%s/%02d" % (dir, bundle.sec_no))
        
class CCGbankStyleOutput(Filter, OutputCCGbankDerivation):
    def __init__(self, outdir):
        OutputCCGbankDerivation.__init__(self)
        self.outdir = outdir
        
    def accept_derivation(self, bundle):
        self.write_derivation(bundle)
