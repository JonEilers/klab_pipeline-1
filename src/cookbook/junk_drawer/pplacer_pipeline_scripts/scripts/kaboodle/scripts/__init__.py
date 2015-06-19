import os.path

def extant_file(s):
    if not os.path.isfile(s):
        raise ValueError("Does not exist: {0}".format(s))
    return s

def floatish(s):
    float(s)
    return s

def joiner(base):
    """
    Return a function emulating os.path.join starting from base
    """
    def p(*args):
        return os.path.join(base, *args)
    return p

def stripext(s, basename=True):
    if basename:
        s = os.path.basename(s)
    return os.path.splitext(s)[0]
