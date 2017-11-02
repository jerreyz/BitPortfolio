
def TerminalDecorator(func):
        def func_wrapper(name):
            return ('>>%20<<').format(func(self))
        return func_wrapper    