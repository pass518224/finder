import logging

logger = logging.getLogger(__name__)

class Module(object):
    """docstring for Mo"""
    def __init__(self):
        self.funcs = {
            "FINDER_START" : [],
            "SOLVING_START" : [],
            "SOLVING_SUCCESS" : [],
            "SOLVING_FAIL" : [],
            "FINDER_END" : []
        }

    def add(self, name):
        module = __import__("modules." + name, globals(), locals(), name)
        logger.info("module [{}] loading".format(name))
        if hasattr(module, "module_init") :
            descriptor = module.module_init()
            for hook, func in descriptor.items():
                try:
                    self.funcs[hook].append(func)
                except KeyError as e:
                    logger.warn("in [{}]> unknown hook point: [{}]".format(name, hook))
                    exit()
        else:
            logging.warn("non found 'module_init' function of module:[{}]".format(name))

    def call(self, hookName, *args):
        if  self.funcs[hookName]:
            for func in self.funcs[hookName]:
                func(*args)

instance = None
def getModule():
    global instance
    if  not instance:
        instance = Module()
    return instance
