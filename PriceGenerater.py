import random
class PriceGenerater(object):
    def __init__(self):
        return

    def generatePriceBasic(self, maxPrice, minPrice):
        out = []
        for i in xrange(365):
            out.append((i, random.randint(maxPrice, minPrice)))
        return out

            

