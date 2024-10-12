
def set_calcs_sodimac(item):
    if item.guide == None:
        item.guide =  1500
    if item.commission == None:
        item.commission = 2
    if item.shipment_cost == None:
        item.shipment_cost = 6900
    pricePublication = (item.MainProducts.price_base/(100-item.commission)*100) + item.guide + item.shipment_cost
    return  pricePublication, item.guide, item.commission , item.shipment_cost