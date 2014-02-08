from .decorators import accepts

@accepts(str)
def t(x):
    return x

