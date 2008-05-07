from itertools import izip, islice, tee
from copy import copy

def each_pair(seq):
    '''Given an iterator (i0, i1, i2, ...), returns an iterator ((i0, i1), (i1, i2), ...).'''
    s1, s2 = tee(seq)
    return izip(s1, islice(s2, 1, None))

def flatten(seq):
    '''Recursively flattens a sequence such as (A, (B, C, (D, E))) into a non-nested
sequence (A, B, C, D, E).'''
    for element in iter(seq):
        if isinstance(element, (list, tuple)):
            for subelement in flatten(element):
                yield subelement
        else:
            yield element
            
def reject(orig_seq, pred):
    '''Given a sequence and a predicate, this accepts only elements which do not satisfy the
predicate.'''
    orig_seq, seq = tee(orig_seq, 2)
    
    return (element for element in seq if not pred(element))