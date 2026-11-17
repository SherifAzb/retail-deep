import pandas as pd

rec = pd.read_csv('product_recommendations.csv')
off = pd.read_csv('product_offers.csv').set_index('Product_ID')
bun = pd.read_csv('product_bundles.csv', encoding='utf-8-sig')
catalog = pd.read_csv('products_catalog.csv', encoding='utf-8-sig').set_index('Product_ID')
HIDDEN = ['P035']
names = rec.drop_duplicates('Product_ID').set_index('Product_ID')['Product']
top_sellers = off.sort_values('Lines', ascending=False).head(3)['Product'].tolist()


def suggestions(product_id):
    r = rec[(rec['Product_ID'] == product_id) & (rec['Confidence'] >= 0.2)].sort_values('Confidence', ascending=False)
    return [{'name': x['Suggested'], 'share': float(x['Confidence'])} for _, x in r.iterrows()]


def offer(product_id):
    o = off.loc[product_id]
    return {'share': float(o['Discount_Share']), 'avg': float(o['Avg_Discount'])}


def bundles(product_id):
    out = []
    for _, b in bun[bun['Product_ID'] == product_id].iterrows():
        out.append({
            'items': b['Bundle'].split(' + '),
            'share': float(b['Share_of_Product_Invoices']),
            'regular': float(b['Regular_Price']),
            'offer': float(b['Offer_Price']),
            'discount': float(b['Suggested_Discount']),
        })
    return out


def categories():
    return sorted(catalog.drop(HIDDEN, errors='ignore')['Category'].unique())


def products_in(category=None):
    c = catalog.drop(HIDDEN, errors='ignore')
    if category:
        c = c[c['Category'] == category]
    return c.sort_values('Product').index.tolist()


def info(product_id):
    c = catalog.loc[product_id]
    return {'category': c['Category'], 'price': float(c['Price'])}
