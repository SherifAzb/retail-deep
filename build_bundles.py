import sys
from itertools import combinations
import numpy as np
import pandas as pd
import scipy.sparse as sp

data_path = sys.argv[1] if len(sys.argv) > 1 else 'data.csv'
MIN_PARTNER_CONF = 0.2
MIN_BUNDLE_SHARE = 0.10
MIN_BUNDLE_INVOICES = 200

rec = pd.read_csv('product_recommendations.csv')
names = rec.drop_duplicates('Product_ID').set_index('Product_ID')['Product']

d = pd.read_csv(data_path, usecols=['Transaction_ID', 'Product_ID', 'Date', 'Unit_Price', 'Discount'], parse_dates=['Date'])
price = d[d['Date'] >= d['Date'].max() - pd.Timedelta(days=30)].groupby('Product_ID')['Unit_Price'].median()

t = d['Transaction_ID'].astype('category')
p = d['Product_ID'].astype('category')
d['t'] = t.cat.codes
pids = list(p.cat.categories)
n = len(t.cat.categories)
X = sp.csr_matrix((np.ones(len(d)), (d['t'], p.cat.codes)), shape=(n, len(pids)))
X.data[:] = 1
B = X.toarray() > 0
count = B.sum(0)
share = count / n
col = {pid: k for k, pid in enumerate(pids)}

rows = []
for pid in names.index:
    partners = rec[(rec['Product_ID'] == pid) & (rec['Confidence'] >= MIN_PARTNER_CONF)].sort_values('Confidence', ascending=False)['Suggested_ID'].head(4).tolist()
    if not partners:
        continue
    i = col[pid]
    found = []
    for a, b in combinations(partners, 2):
        mask = B[:, i] & B[:, col[a]] & B[:, col[b]]
        k = int(mask.sum())
        if k >= MIN_BUNDLE_INVOICES and k / count[i] >= MIN_BUNDLE_SHARE:
            lift = (k / n) / (share[i] * share[col[a]] * share[col[b]])
            found.append(([pid, a, b], mask, k, lift))
    found = sorted(found, key=lambda x: -x[2])[:2]
    if not found:
        a = partners[0]
        mask = B[:, i] & B[:, col[a]]
        k = int(mask.sum())
        lift = (k / n) / (share[i] * share[col[a]])
        found = [([pid, a], mask, k, lift)]
    for items, mask, k, lift in found:
        lines = d[mask[d['t'].values] & d['Product_ID'].isin(items)]
        disc = lines[lines['Discount'] > 0]
        share_disc = len(disc) / len(lines)
        avg_disc = disc['Discount'].mean() if len(disc) else 0.0
        suggested = round(avg_disc / 0.05) * 0.05
        regular = float(sum(price[x] for x in items))
        rows.append({
            'Product_ID': pid, 'Product': names[pid],
            'Bundle_IDs': ' + '.join(items), 'Bundle': ' + '.join(names[x] for x in items),
            'Size': len(items), 'Invoices': k, 'Share_of_Product_Invoices': round(k / count[i], 4),
            'Lift': round(lift, 2), 'Regular_Price': round(regular, 2),
            'Discount_Share': round(share_disc, 4), 'Avg_Discount': round(avg_disc, 4),
            'Suggested_Discount': round(suggested, 2), 'Offer_Price': round(regular * (1 - suggested), 2),
        })

out = pd.DataFrame(rows)
out.to_csv('product_bundles.csv', index=False, encoding='utf-8-sig')
print(len(out), 'bundles for', out['Product_ID'].nunique(), 'products')
print(out[out['Product_ID'] == 'P001'].T)
