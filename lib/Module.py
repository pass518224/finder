import logging

logger = logging.getLogger(__name__)

class Module(object):
    """Module loader
        Get modules name and place hook functions at the corresponding place.
        The modules can hook at default hook point.
        while the solving, the hook point triggered with corresponding arugments.

        The path of modules is at "FINDER/modules/"
    """
    def __init__(self):
        self.funcs = {
            "FINDER_START" : [],
            "SOLVING_START" : [],
            "SOLVING_SUCCESS" : [],
            "SOLVING_FAIL" : [],
            "FINDER_END" : []
        }
        self.modules = set()

    def add(self, name):
        """
            Add modules to module system.
        """
        if  name in self.modules:
            return
        module = __import__("modules." + name, globals(), locals(), name)
        logger.info("Load module === {} ===".format(name))
        if hasattr(module, "module_init") :
            descriptor = module.module_init()
            if  type(descriptor) != dict:
                logger.warn("return of module_init must be a dict of function pointer, {} given.".format(type(descriptor)))
                exit()
            for hook, func in descriptor.items():
                try:
                    self.funcs[hook].append(func)
                except KeyError as e:
                    logger.warn("in [{}]> unknown hook point: [{}]".format(name, hook))
                    exit()
        else:
            logging.warn("non found 'module_init' function of module:[{}]".format(name))
        self.modules.add(name)

    def call(self, hookName, *args):
        if  self.funcs[hookName]:
            for func in self.funcs[hookName]:
                func(*args)

instance = None
def getModule():
    """
        return instance of module system.

        All actions of modules should through this function.
    """
    global instance
    if  not instance:
        instance = Module()
    return instance
