import logging
import Parcel

logger = logging.getLogger(__name__)

class Transaction(object):
    """
        transaction type contain pid, tid, parcel
    """
    def __init__(self, info):
        self.info = info
        if  "data" in info:
            if  int(info["length"]) *2 > info["data"]:
                raise TransactionError("Unmatched length with data")
            try:
                self.parcel = Parcel.Parcel(info["data"][:int(info["length"])*2])
                del info["data"]
            except TypeError:
                raise TransactionError("invalid hex: " + info["data"])
        else:
            raise TransactionError("missed data field in info")


        for key, val in info.items():
            setattr(self, key, val)
        del self.info["type"]


    def __str__(self):
        return "{type}: {others}\n{parcel}".format(type = self.type, others = self.info, parcel = self.parcel)


class TransactionError(Exception):
    """Transaction error"""
    pass
        
        
