# Chinese CCGbank conversion
# ==========================
# (c) 2008-2012 Daniel Tse <cncandc@gmail.com>
# University of Sydney

# Use of this software is governed by the attached "Chinese CCGbank converter Licence Agreement"
# supplied in the Chinese CCGbank conversion distribution. If the LICENCE file is missing, please
# notify the maintainer Daniel Tse <cncandc@gmail.com>.

import sys, copy

from munge.util.config import config
config.set(show_vars=True, curly_vars=True)

from munge.cats.headed.nodes import AtomicCategory
from munge.cats.headed.parse import *
from munge.cats.cat_defs import NP, N
from munge.util.err_utils import *
from munge.trees.traverse import leaves

from apps.util.echo import echo

def variables():
    '''Returns an iterator over variable names. The first variable name returned is _,
for the outermost variable.'''
    # C&C only supports up to variable F
    # We add variables G, H to prevent two failures
    # (5:27(12) and 27:97(12)) which run out of variables
    return iter('_YZWVUTRQABCDEFGH')

def is_modifier(cat):
    '''Returns whether _cat_ is of the form X/X.'''
    return cat.left.equal_respecting_features(cat.right) and cat.left.slot.var is cat.right.slot.var

def is_np_n(cat):
    '''Returns whether _cat_ is the category NP/N.'''
    return cat.left == NP and cat.right == N
    
C = parse_category
Exceptions = (
    # relcl categories with N/NP distinction
    (C(r'(N/N)\(S[dcl]\NP)'), C(r'((N{%E}/N{%E}){%_}\(S[dcl]{%F}\NP{%E}){%F}){%_}')),
    (C(r'(N/N)\(S[dcl]/NP)'), C(r'((N{%E}/N{%E}){%_}\(S[dcl]{%F}/NP{%E}){%F}){%_}')),
    
    (C(r'(NP/NP)\(S[dcl]\NP)'), C(r'((NP{%E}/NP{%E}){%_}\(S[dcl]{%F}\NP{%E}){%F}){%_}')),
    (C(r'(NP/NP)\(S[dcl]/NP)'), C(r'((NP{%E}/NP{%E}){%_}\(S[dcl]{%F}/NP{%E}){%F}){%_}')),
    (C(r'((NP/NP)/(NP/NP))\(S[dcl]/NP)'), C(r'( ((NP{%G}/NP{%G}){%E}/(NP{%G}/NP{%G}){%E}){%_}   \(S[dcl]{%F}/NP{%E}){%F}){%_}')),
    (C(r'((NP/NP)/(NP/NP))\(S[dcl]\NP)'), C(r'( ((NP{%G}/NP{%G}){%E}/(NP{%G}/NP{%G}){%E}){%_}   \(S[dcl]{%F}\NP{%E}){%F}){%_}')),
    (C(r'(S[dcl]\NP)/(S[dcl]\NP)'), C(r'((S[dcl]{%_}\NP{%F}){%_}/(S[dcl]{%E}\NP{%F}){%E}){%_}')),
    # gapped long bei
    (C(r'((S[dcl]\NP)/((S[dcl]\NP)/NP))/NP'), C(r'(((S[dcl]{%_}\NP{%F}){%_}/((S[dcl]{%E}\NP{%D}){%E}/NP{%F}){%E}){%_}/NP{%D}){%_}')),
    # non-gapped long bei
    (C(r'((S[dcl]\NP)/(S[dcl]\NP))/NP'), C(r'(((S[dcl]{%_}\NP{%D}){%_}/(S[dcl]{%E}\NP{%F}){%E}){%_}/NP{%F}){%_}')),
    # gapped short bei
    (C(r'(S[dcl]\NP)/((S[dcl]\NP)/NP)'), C(r'((S[dcl]{%_}\NP{%F}){%_}/((S[dcl]{%D}\NP{%E}){%D}/NP{%F}){%D}){%_}')),
    # non-gapped short bei
    # alias SB because of conflict with control/raising category
    (C(r'(S[dcl]\NP)/(S[dcl]\NP)~SB'), C(r'((S[dcl]{%_}\NP{%Y}){%_}/(S[dcl]{%W}\NP{%Z}){%W}){%_}~SB')),
    
    (C(r'(S[dcl]\NP)/(S[dcl]/NP)'), C(r'((S[dcl]{%_}\NP{%Y}){%_}/(S[dcl]{%Z}/NP{%Y}){%Z}){%_}')),

    # hacks
    # not a modifier category:
    (C(r'((S[dcl]\NP)/(S[dcl]\NP))/((S[dcl]\NP)/(S[dcl]\NP))'),
     C(r'(((S[dcl]{%F}\NP{%E}){%F}/(S[dcl]{%D}\NP{%E}){%D}){%F}/((S[dcl]{%F}\NP{%E}){%F}/(S[dcl]{%D}\NP{%E}){%D}){%F}){%_}')),
     
    (C(r'((S[dcl]\NP)/NP)/((S[dcl]\NP)/NP)'),
     C(r'(((S[dcl]{%F}\NP{%E}){%F}/NP{%D}){%F}/((S[dcl]{%F}\NP{%E}){%F}/NP{%D}){%F}){%_}')),
     
    (C(r'(((S[dcl]\NP)/(S[dcl]\NP))/NP)/(((S[dcl]\NP)/(S[dcl]\NP))/NP)'),
     C(r'((((S[dcl]{%F}\NP{%E}){%F}/(S[dcl]{%D}\NP{%C}){%D}){%F}/NP{%B}){%F}/(((S[dcl]{%F}\NP{%E}){%F}/(S[dcl]{%D}\NP{%C}){%D}){%F}/NP{%B}){%F}){%_}')),
     
    (C(r'(((S[dcl]\NP)/(S[dcl]\NP))\((S[dcl]\NP)/(S[dcl]\NP)))/((S[dcl]\NP)/(S[dcl]\NP))'),
     C(r'((((S[dcl]{%C}\NP{%D}){%C}/(S[dcl]{%E}\NP{%D}){%E}){%C}\((S[dcl]{%C}\NP{%D}){%C}/(S[dcl]{%B}\NP{%D}){%B}){%C}){%C}/((S[dcl]{%F}\NP{%D}){%F}/(S[dcl]{%B}\NP{%D}){%B}){%B}){%_}')),
     
    #(C(r'((S[dcl]\NP)/((S[dcl]\NP)/NP))/NP'),
    # C(r'(((S[dcl]{%_}\NP{%F}){%_}/((S[dcl]{%E}\NP{%D}){%E}/NP{%F}){%E}){%_}/NP{%D}){%_}')),
     
    # make sure things which look like modifier categories but aren't are given the right markedup
    # these are all attested categories of the form (S[dcl]\S[dcl])/$
    # TODO: we don't need to do this: just define a mapping for S[dcl]\S[dcl] and anything that uses it should
    #       pick up correct markedup
    (C(r'(S[dcl]\S[dcl])/NP'), C(r'((S[dcl]{%_}\S[dcl]{%E}){%_}/NP{%F}){%_}')),
    (C(r'(S[dcl]\S[dcl])/(S[dcl]\NP)'), C(r'((S[dcl]{%_}\S[dcl]{%E}){%_}/(S[dcl]{%F}\NP{%D}){%F}){%_}')),
    (C(r'(S[dcl]\S[dcl])/S[dcl]'), C(r'((S[dcl]{%_}\S[dcl]{%E}){%_}/S[dcl]{%F}){%_}')),
    (C(r'(S[dcl]\S[dcl])/PP'), C(r'((S[dcl]{%_}\S[dcl]{%E}){%_}/PP{%F}){%_}')),
    (C(r'(S[dcl]\S[dcl])/QP'), C(r'((S[dcl]{%_}\S[dcl]{%E}){%_}/QP{%F}){%_}')),
    (C(r'(S[dcl]\S[dcl])/M'), C(r'((S[dcl]{%_}\S[dcl]{%E}){%_}/M{%F}){%_}')),
    (C(r'S[dcl]\S[dcl]'), C(r'(S[dcl]{%_}\S[dcl]{%E}){%_}')),
    
    (C(r'(S\S)\(S\S)'), C(r'((S{%F}\S{%E}){%F}\(S{%F}\S{%E}){%F}){%_}')),
    (C(r'(S\S)/(S\S)'), C(r'((S{%F}\S{%E}){%F}/(S{%F}\S{%E}){%F}){%_}')),
    (C(r'(S\S)/(S\NP)'), C(r'((S{%F}\S{%E}){%F}/(S{%F}\NP{%D}){%F}){%_}')),
    (C(r'(S\LCP)/(S\NP)'), C(r'((S{%F}\LCP{%E}){%F}/(S{%F}\NP{%D}){%F}){%_}')),
    (C(r'(S\QP)/(S\NP)'), C(r'((S{%F}\QP{%E}){%F}/(S{%F}\NP{%D}){%F}){%_}')),
    
    (C(r'((S\S)/(S\NP))/NP'), C(r'(((S{%F}\S{%E}){%F}/(S{%D}\NP{%C}){%D}){%_}/NP{%B}){%_}')),

    (C(r'S[q]\S[dcl]'), C(r'(S[q]{%F}\S[dcl]{%F}){%_}')),

    # short bei for bei VPdcl/VPdcl (wo bei qiangzhi)
    (C(r'(S[dcl]\NP)/(((S[dcl]\NP)/(S[dcl]\NP))/NP)'), C(r'((S[dcl]{%_}\NP{%F}){%_}/(((S[dcl]{%E}\NP{%F}){%E}/(S[dcl]{%D}\NP{%F}){%D}){%E}/NP{%F}){%E}){%_}')),

    # long bei for bei NP VPdcl/VPdcl (wo bei ta qiangzhi)
    (C(r'((S[dcl]\NP)/(((S[dcl]\NP)/(S[dcl]\NP))/NP))/NP'),
     C(r'(((S[dcl]{%_}\NP{%F}){%_}/(((S[dcl]{%C}\NP{%E}){%C}/(S[dcl]{%D}\NP{%F}){%D}){%C}/NP{%F}){%C}){%_}/NP{%E}){%_}')),
      #C(r'(((S[dcl]{%_}\NP{%F}){%_}/(((S[dcl]{%D}\NP{%E}){%D}/(S[dcl]{%C}\NP{%F}){%C}){%D}/NP{%F}){%D}){%_}/NP{%E}){%_}')),
    
    # VPdcl/VPdcl modifier category fix
    (C(r'(((S[dcl]\NP)/(S[dcl]\NP))/NP)/(((S[dcl]\NP)/(S[dcl]\NP))/NP)'), 
     C(r'((((S[dcl]{%E}\NP{%F}){%E}/(S[dcl]{%D}\NP{%F}){%D}){%E}/NP{%F}){%C}/(((S[dcl]{%E}\NP{%F}){%E}/(S[dcl]{%D}\NP{%F}){%D}){%E}/NP{%F}){%C}){%_}')),
    
    # gei category fix (NP gei NP NP VP e.g. tamen gei haizi jihui xuanze 10:53(34))
    (C(r'(((S[dcl]\NP)/(S[dcl]\NP))/NP)/NP'),
     C(r'((((S[dcl]{%_}\NP{%C}){%_}/(S[dcl]{%D}\NP{%E}){%D}){%_}/NP{%F}){%_}/NP{%E}){%_}')),

    # this category is probably not correct
    (C(r'((S[dcl]\NP)/(S[dcl]\NP))/S[dcl]'),
     C(r'(((S[dcl]{%_}\NP{%C}){%_}/(S[dcl]{%D}\NP{%E}){%D}){%_}/S[dcl]{%F}){%_}')),
    
    # nor this (20:31(7))
    (C(r'((S[dcl]\NP)/(S[dcl]\NP))/PP'),
     C(r'(((S[dcl]{%_}\NP{%F}){%_}/(S[dcl]{%D}\NP{%E}){%D}){%_}/PP{%C}){%_}')),     
)

# sanity check to make sure all manual markedup slots are filled in
for (frm, to) in Exceptions:
    for subcat in to.nested_compound_categories():
        assert subcat.slot.var != AtomicCategory.NoVariableSentinel, \
            "Markedup for category %s contains unspecified var" % to

def get_cached_category_for(cat, lex, vars):
    '''If _cat_ matches one of the mappings defined in Exceptions, returns a copy of
the cached category, filling in its outermost variable's lex with _lex_.'''
    for frm, to in Exceptions:
        if cat.equal_respecting_features_and_alias(frm):
            result = copy.deepcopy(to)
            for subcat in result.nested_compound_categories():
                # rewrite a variable name beginning with % with an available
                # variable (if the markedup has been parsed correctly, all
                # mentions of that variable will be updated)
                if subcat.slot.var.startswith('%'):
                    subcat.slot.var = vars.next()
            return result
    return None

n = 1
def label(cat, vars=None, lex=None):
    '''Labels the category _cat_ using the markedup labelling algorithm, with
available variable labels _vars_ and lexical item _lex_.'''
    global n
        
    available = vars or variables()
    cached = get_cached_category_for(cat, lex, vars=available)
    if cached: 
        cp = copy.deepcopy(cached)
        return cp
    
    if cat.slot.var == AtomicCategory.NoVariableSentinel:
        suffix = str(n) if config.debug_vars else ''
        cat.slot.var = (available.next() + suffix)

    if cat.is_complex():
        c = cat
        while c.is_complex() and not (is_modifier(c) or is_np_n(c)):
            c.left.slot = cat.slot
            c = c.left

        if is_modifier(cat):
            cat._left = label(cat.left, available, lex)
            cat._right = copy.copy(cat._left)

        elif is_np_n(cat):
            cat._left = label(cat.left, available, lex)
            cat._right.slot = cat._left.slot

        else:
            cat._left = label(cat.left, available, lex)
            cat._right = label(cat.right, available, lex)

    n += 1
    return cat

PREFACE = "# this file was generated by the following command(s):"
def write_markedup(cats, file):
    print >>file, PREFACE
    print >>file
    
    for cat in sorted(cats):
        print >>file, cat.__repr__(suppress_vars=True)
        print >>file, "\t", 0, cat.__repr__(suppress_alias=True)
        print >>file

def naive_label_derivation(root):
    '''Applies the markedup labelling algorithm to each leaf under _root_.'''
    for leaf in leaves(root):
        leaf.cat = label(leaf.cat, lex=leaf.lex)
        # pre-populate the outermost slot with the lexical item
        leaf.cat.slot.head.lex = leaf.lex
        
    return root

if __name__ == '__main__':
    # for cat in cats:
    #     print label(cat)

    import sys
    write_markedup(map(label, map(parse_category, sys.stdin.xreadlines())), sys.stdout)
    # 
    # print label(parse_category(r'((S\NP)/(S\NP))/NP'))
    # print label(parse_category(r'(S\NP)/(S\NP)'))
    # print label(parse_category(r'(S[dcl]\NP)/NP'))
    # print label(parse_category(r'((S[dcl]\NP)/NP)/PP'))
    # print label(parse_category(r'(((S[dcl]\NP)/NP)/NP)/PP'))
    # print label(parse_category(r'(S[dcl]\NP)/(S[dcl]\NP)'))
    # print label(parse_category(r'N/N'))
    # print label(parse_category(r'(N/N)/(N/N)'))
    # print label(parse_category(r'((N/N)/(N/N))/((N/N)/(N/N))'))
    # print label(parse_category(r'PP/LCP'))
    # print label(parse_category(r'NP'))
    # print label(parse_category(r'(N/N)\NP'))
    # print label(parse_category(r'(NP\NP)/(S[dcl]\NP)'))
    # print label(parse_category(r'NP/N'))
    # print label(parse_category(r'(N/N)\(S[dcl]/NP)'))
