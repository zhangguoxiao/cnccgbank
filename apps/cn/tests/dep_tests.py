# Chinese CCGbank conversion
# ==========================
# (c) 2008-2012 Daniel Tse <cncandc@gmail.com>
# University of Sydney

# Use of this software is governed by the attached "Chinese CCGbank converter Licence Agreement"
# supplied in the Chinese CCGbank conversion distribution. If the LICENCE file is missing, please
# notify the maintainer Daniel Tse <cncandc@gmail.com>.

import unittest

from itertools import imap
from apps.cn.mkdeps import mkdeps, UnificationException, IndexSeparator
from apps.cn.mkmarked import naive_label_derivation
from munge.ccg.parse import parse_tree

def parse_gsdeps(line):
    return set(tuple(dep.split('|')) for dep in line.split())

class DepTests(unittest.TestCase):
    def check(self, derivs_file, gs_file):
        with open(derivs_file) as f:
            with open(gs_file) as gs:
                file = f.readlines()
                gsdeps_file = gs.readlines()
            
                while file and gsdeps_file:
                    _, deriv = file.pop(0), file.pop(0)
                    gsdeps_line = gsdeps_file.pop(0)
                    
                    if deriv.startswith('#'): continue
                    
                    t = naive_label_derivation(parse_tree(deriv))
                    # only take the first two elements (filler lex, arg lex)
                    deps = set(imap(lambda v: tuple(e.split(IndexSeparator)[0] for e in v[0:2]), mkdeps(t)))
                    gsdeps = parse_gsdeps(gsdeps_line)
                    
                    try:
                        self.assertEqual(deps, gsdeps)
                    except AssertionError:
                        print "EXPECTED\n-------"
                        for depl, depr in sorted(gsdeps):
                            print depl, depr
                        print "GOT\n---"
                        for depl, depr in sorted(deps):
                            print depl, depr
                        print "DIFF\n----"
                        print "false negatives: %s" % ' '.join('|'.join((u, v)) for u, v in list(set(gsdeps) - set(deps)))
                        print "false positives: %s" % ' '.join('|'.join((u, v)) for u, v in list(set(deps) - set(gsdeps)))
                            
                        raise
        
    def testBasic(self):
        self.check('apps/cn/tests/test1.ccg', 'apps/cn/tests/test1.gs')
        self.check('apps/cn/tests/test2.ccg', 'apps/cn/tests/test2.gs')
        self.check('apps/cn/tests/test3.ccg', 'apps/cn/tests/test3.gs')
        self.check('apps/cn/tests/test4.ccg', 'apps/cn/tests/test4.gs')
        self.check('apps/cn/tests/passives.ccg', 'apps/cn/tests/passives.gs')
        self.check('apps/cn/tests/vnv.ccg', 'apps/cn/tests/vnv.gs')
#        self.check('final/chtb_9992.fid', 'apps/cn/tests/blah.gs')
                    
if __name__ == '__main__':
    unittest.main()