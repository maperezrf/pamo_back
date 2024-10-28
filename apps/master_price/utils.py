from apps.master_price.connections_google_sheets import ConnectionsGoogleSheets


def set_calcs_sodimac(item):
    if item.guide == None:
        item.guide =  1500
    if item.commission == None:
        item.commission = 2
    if item.shipment_cost == None:
        item.shipment_cost = 6900
    pricePublication = (item.MainProducts.price_base/(100-item.commission)*100) + item.guide + item.shipment_cost
    return  pricePublication, item.guide, item.commission , item.shipment_cost


def read_seets(id):
    conn = ConnectionsGoogleSheets()
    file = conn.read_file(id)
    sheets = conn.get_all_sheets(file)
    sheets_dic =[{'name':i.title, 'id':i.id} for i in  sheets]
    df = conn.sheet_to_df(file)
    df = df[[i for i in df.columns if i != '']]
    df = df.loc[(df['sku'] != '')].reset_index(drop=True)
    return df, file, sheets_dic