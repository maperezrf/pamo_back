from apps.master_price.connections_google_sheets import ConnectionsGoogleSheets
from apps.master_price.models import MainProducts

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

def update_status_bot(item, progress, status):
    item.progress = progress
    item.status = status
    item.save() 

def handle_init_process(item, init):
    item.init = init
    item.save()

def create_product(products, model, item_bot):
    progress = 20
    cant = len(products)
    acum_percent = 80/cant
    for index, i in enumerate(products):
        progress += acum_percent
        update_status_bot(item_bot, progress,  status = f'Actualizando base: {index+1}/{cant}')
        item, _ = model.objects.get_or_create(publication=i['publication'])
        main_product = MainProducts.objects.filter(sku=i['sku']).first()
        if main_product:
            item.main_product = main_product
        item.publication = i.get('publication', None) 
        item.stock = i.get('stock', 0) 
        item.url_publication = i.get('url_publication', None) 
        item.commission = i.get('commission', 0)
        item.shipment_cost = i.get('shipment_cost', 0)
        item.status = i.get('status', 0)
        item.Price = i.get('Price', 0)
        item.save()

