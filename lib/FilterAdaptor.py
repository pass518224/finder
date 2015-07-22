import logging
import ConfigParser

import TransactionFilter

logger = logging.getLogger(__name__)

class FilterAdaptor(object):
    """docstring for FilterAdaptor"""
    def __init__(self, args):
        self.factory = TransactionFilter.FilterFactory()

        if  args.black_list:
            self.blacklist(args.black_list)

        if  args.contain or args.sender or args.receiver:
            self.nameFilter(args)
        
    def blacklist(self, fd):
        #print fd.read()
        parser = ConfigParser.RawConfigParser(allow_no_value=True)
        parser.readfp(fd)
        for section in parser.sections():
            for item in parser.items(section):
                self.factory.addBlacklist(section, item[0])

    def nameFilter(self, args):
        if  args.contain:
            self.factory.roleFilter(contain=args.contain)
        elif args.sender:
            self.factory.roleFilter(sender=args.sender)
        elif args.receiver:
            self.factory.roleFilter(receiver=args.receiver)

    def getFilter(self):
        return self.factory.getFilter()

