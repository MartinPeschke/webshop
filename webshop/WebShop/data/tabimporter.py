mapping = dict([('Line','Line.line_ref'),
		('ArticleFamily','ArticleFamily.af_ref'),
		('ArticleReference','Article.a_ref'),
		('OptionReference','ArticleOption.ao_ref'),

#		('ProviderID','ArticleOption.AOSourcing.1.provider_id'),
#		('MatchCode','ArticleOption.AOSourcing.1.matchCode'),
#		('ProviderPrice','ArticleOption.AOSourcing.1.sourcePrice'),
#		('MinSourceQty','ArticleOption.AOSourcing.1.minSourceQty'),
#		('Provider2ID','ArticleOption.AOSourcing.2.provider_id'),
#		('MatchCode2','ArticleOption.AOSourcing.2.matchCode'),
#		('ProviderPrice2','ArticleOption.AOSourcing.2.sourcePrice'),
#		('MinSourceQty2','ArticleOption.AOSourcing.2.minSourceQty'),
#		('Composition','ArticleOption.composition'),
		('LowStockQty','ArticleOption.lowStockQty'),

#		('StockQty','ArticleOption.AOStockBatch.1.stockQty'),
#		('StockQtyComment','ArticleOption.AOStockBatch.1.comment'),
#		('StockQtyBasement','ArticleOption.AOStockBatch.2.stockQty'),
#		('StockQtyBasementComment','ArticleOption.AOStockBatch.2.comment'),

		('HighStockQty','ArticleOption.highStockQty'),
		('SubImageCode','ArticleOption.subImgCode'),
		('RetailUnitPrice','Article.Pricing.0[E].price'),
		('ResellerUnitPrice','Article.Pricing.1[K].price'),
		('ResellerUnitDiscountPrice','Article.Pricing.2[K].price'),
		('DiscountQty','Article.Pricing.2[K].discountQty'),
		('Discount 2 Price','Article.Pricing.3[K].price'),
		('Discount 2 Quantity','Article.Pricing.3[K].discountQty'),
		('PartnerPrice','Article.Pricing.4[P].price'),

		('Weight','Article.weight'),

		('Thickness','Article.thickness'),
		('LengthDiameter','Article.diameter_len'),
		('Ballsize1','Article.ball_size1'),
		('Ballsize2','Article.ball_size2'),

		('Size1','Article.diameter_len'),
		('Size2','Article.ball_size1'),
		('Size3','Article.ball_size2'),
		('Pcs','Article.thickness'),

		('Tags1','Article.tags'),
		('Tags2','Article.tags'),
		('Tags3','Article.tags'),
		('Tags4','Article.tags'),
		('Tags5','Article.tags'),
		('BestBefore','Article.bestBefore'),

		('Type','ArticleFamily.art_type_default'),
		('Type(de)','ArticleFamily.art_type.de'),
		('Type(fr)','ArticleFamily.art_type.fr'),
		('Type(it)','ArticleFamily.art_type.it'),
		('Type(es)','ArticleFamily.art_type.es'),
		('Type(pl)','ArticleFamily.art_type.pl'),
		('Description','ArticleFamily.desc_I18N_default'),
		('Description(de)','ArticleFamily.desc.de'),
		('Description(fr)','ArticleFamily.desc.fr'),
		('Description(it)','ArticleFamily.desc.it'),
		('Description(es)','ArticleFamily.desc.es'),
		('Description(pl)','ArticleFamily.desc.pl'),
		('Description(ch)','ArticleFamily.desc.ch'),

		('BodyParts','ArticleFamily.body_part'),
		('News','ArticleFamily.inWebshopNew'),
		('Sale','ArticleFamily.inWebshopSale'),
		('InWebshop','ArticleFamily.inWebshop'),
		('SizeIn','ArticleFamily.measureUnit')])


import pprint

f = open('20080211_FASHIONSHOP2008.txt','r')

f.seek(0)
header = [mapping.get(word, '?%s'%word) for word in f.readline().strip('\n').split('\t')]

for line in f:
	row = dict(filter(lambda x: x[1], zip(header, [(l and (l[0] == '"' and l[-1]== '"' and l[1:-1]) or l).strip('\n').replace('""','"') for l in line.split('\t')])))
	pprint.pprint(row)