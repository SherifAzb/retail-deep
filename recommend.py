import pandas as pd

rec = pd.read_csv('product_recommendations.csv')
off = pd.read_csv('product_offers.csv').set_index('Product_ID')
bun = pd.read_csv('product_bundles.csv', encoding='utf-8-sig')
names = rec.drop_duplicates('Product_ID').set_index('Product_ID')['Product']
top_sellers = off.sort_values('Lines', ascending=False).head(3)['Product'].tolist()


def suggest(product_id):
    r = rec[(rec['Product_ID'] == product_id) & (rec['Confidence'] >= 0.2)]
    return [f"{x['Suggested']}  ({x['Confidence']:.0%} من الفواتير اللي فيها {x['Product']} بيكون فيها كمان {x['Suggested']})" for _, x in r.iterrows()]


def offer(product_id):
    o = off.loc[product_id]
    return f"المنتج ده اتباع بخصم في {o['Discount_Share']:.0%} من الحالات، ومتوسط الخصم {o['Avg_Discount']:.0%}"


def bundles(product_id):
    out = []
    for _, b in bun[bun['Product_ID'] == product_id].iterrows():
        out.append(
            f"{b['Bundle']}\n"
            f"  بيتشتروا مع بعض في {b['Share_of_Product_Invoices']:.0%} من فواتير {b['Product']}\n"
            f"  السعر العادي {b['Regular_Price']:.0f} ج، وبعد خصم {b['Suggested_Discount']:.0%} (متوسط الخصم اللي اتعمل فعلاً على الباندل ده) ≈ {b['Offer_Price']:.0f} ج"
        )
    return out


def answer(product_id):
    sug = suggest(product_id)
    bnd = bundles(product_id)
    lines = [f"المنتج: {names[product_id]}", "", "ممكن تشتري معاه:"]
    lines += ['- ' + s for s in sug] if sug else ['- مفيش منتج بيتشرى معاه بشكل واضح في الداتا', '  (الأكتر مبيعاً عموماً: ' + '، '.join(top_sellers) + ')']
    lines += ["", "الباندلات المقترحة:"]
    lines += ['- ' + b for b in bnd] if bnd else ['- مفيش باندل واضح للمنتج ده']
    lines += ["", "العروض: " + offer(product_id)]
    return '\n'.join(lines)
