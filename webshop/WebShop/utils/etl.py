# -*- coding: utf-8 -*-
import simplejson, re
import pprint

DEFAULT_SHOP = 'Piercing'

ANONYMOUS_ROLE = 'F'
LEAST_ROLE = 'E'
NORM_ROLE = 'K'
NO_RIGHTS = [ANONYMOUS_ROLE, 'E', 'X']
HAS_RIGHTS = ['K', 'P', 'M']

#    role : roleName
USER_GROUPS = [
    ('E', 'Retail'),
    ('K', 'Wholesale'),
    ('P', 'Partner'),
    ('M', 'Content Manager'),
]
USER_ROLES = [(ANONYMOUS_ROLE, 'Anonymous')] + USER_GROUPS + [('X', 'Disabled')]

userRoles = dict(USER_ROLES)

def deep_import(json):
	from WebShop.apps.service.views.bo import parseJson
	return parseJson(json)

'''
    Main Entry
'''
def process(jsonfile):
    fd = open(jsonfile)
    print 'Loading JSON file...'
    json_data = simplejson.load(fd)
    print 'Data Loaded.'
    deep_import(json_data)

    
def importTabDelimted(shop_ref, tabdelimitedfilename):
    def updateDict(hash, row, key):
        hash.update(dict([(a.replace(key,''),b) for a,b in row.iteritems() if key in a]))
        return hash
    def parsePricings(pricingDict):
        rePricing = re.compile("([0-9])\[([A-Z])\]")
        orderedList = pricingDict.items()
        orderedList.sort()
        pricingDict = {}
        for k,v in orderedList:
            match = rePricing.match(k.split('.')[0])
            if(match):
                pricing = pricingDict.get(match.group(1),{})
                pricing['cg_ref'] = match.group(2)
                pricing[k.split('.')[1]] = v
                pricingDict[match.group(1)] = pricing
        return pricingDict.values()
    
    
    def updateShopDict(shop, row):
        line_ref = row.get('Line.line_ref', None)
        if(line_ref):
            line = shop['lines'].get(line_ref, {'art_types':{}})
            line = updateDict(line, row, 'Line.')
    
            line['name'] = line_ref
            line['inWebshop'] = True
            line['line_ref'] = line_ref.replace(' ', '_').replace('&', '-').replace('/', '_')
    
            at_ref = row.get('ArticleType.en', None)
            if(at_ref):
                at = line['art_types'].get(at_ref, {'families':{}})
                at = updateDict(at, row, 'ArticleType.')
                af_ref = row.get('ArticleFamily.af_ref', None)
                if(af_ref):
                    af = at['families'].get(af_ref, {'articles':{}, 'desc':{}})
                    af = updateDict(af, row, 'ArticleFamily.')
                    af['desc'] = updateDict(af['desc'], row, 'Description.')
                    a_ref = row.get('Article.a_ref', None)
                    if(a_ref):
                        a = af['articles'].get(a_ref, {'options':{}, 'pricings':{}})
                        a = updateDict(a, row, 'Article.')
                        ao_ref = row.get('ArticleOption.ao_ref', None)
                        if(ao_ref):  
                            ao = a['options'].get(ao_ref, {})
                            ao = updateDict(ao, row, 'ArticleOption.')
                            a['options'][ao_ref] = ao
                        pricings = {}
                        a['pricings'] = parsePricings(updateDict(pricings, row, 'Pricing.'))
                        af['articles'][a_ref] = a
                    at['families'][af_ref] = af
                line['art_types'][at_ref] = at
            shop['lines'][line_ref] = line
        return shop

    TABXLSMAPPING = dict([
        ('Line','Line.line_ref'),
        ('ArticleFamily','ArticleFamily.af_ref'),
        ('ArticleReference','Article.a_ref'),
        ('OptionReference','ArticleOption.ao_ref'),
    
    #        ('ProviderID','ArticleOption.AOSourcing.1.provider_id'),
    #        ('MatchCode','ArticleOption.AOSourcing.1.matchCode'),
    #        ('ProviderPrice','ArticleOption.AOSourcing.1.sourcePrice'),
    #        ('MinSourceQty','ArticleOption.AOSourcing.1.minSourceQty'),
    #        ('Provider2ID','ArticleOption.AOSourcing.2.provider_id'),
    #        ('MatchCode2','ArticleOption.AOSourcing.2.matchCode'),
    #        ('ProviderPrice2','ArticleOption.AOSourcing.2.sourcePrice'),
    #        ('MinSourceQty2','ArticleOption.AOSourcing.2.minSourceQty'),
    #        ('Composition','ArticleOption.composition'),
        ('LowStockQty','ArticleOption.lowStockQty'),
    
    #        ('StockQty','ArticleOption.AOStockBatch.1.stockQty'),
    #        ('StockQtyComment','ArticleOption.AOStockBatch.1.comment'),
    #        ('StockQtyBasement','ArticleOption.AOStockBatch.2.stockQty'),
    #        ('StockQtyBasementComment','ArticleOption.AOStockBatch.2.comment'),
    #        ('Tags1','Article.tags'),
    #        ('Tags2','Article.tags'),
    #        ('Tags3','Article.tags'),
    #        ('Tags4','Article.tags'),
    #        ('Tags5','Article.tags'),
        ('HighStockQty','ArticleOption.highStockQty'),
        ('SubImageCode','ArticleOption.subImgCode'),
        ('RetailUnitPrice','Pricing.0[E].price'),
        ('ResellerUnitPrice','Pricing.1[K].price'),
        ('ResellerUnitDiscountPrice','Pricing.2[K].price'),
        ('DiscountQty','Pricing.2[K].discountQty'),
        ('Discount 2 Price','Pricing.3[K].price'),
        ('Discount 2 Quantity','Pricing.3[K].discountQty'),
        ('PartnerPrice','Pricing.4[P].price'),
    
        ('Weight','Article.weight'),
    
        ('Thickness','Article.thickness'),
        ('LengthDiameter','Article.diameter_len'),
        ('Ballsize1','Article.ball_size1'),
        ('Ballsize2','Article.ball_size2'),
    
        ('Size1','Article.diameter_len'),
        ('Size2','Article.ball_size1'),
        ('Size3','Article.ball_size2'),
        ('Pcs','Article.thickness'),
    
    
        ('BestBefore','Article.bestBefore'),
    
        ('logopath','ArticleFamily.logopath'),
        ('Type','ArticleType.en'),
        ('Type(de)','ArticleType.de'),
        ('Type(fr)','ArticleType.fr'),
        ('Type(it)','ArticleType.it'),
        ('Type(es)','ArticleType.es'),
        ('Type(pl)','ArticleType.pl'),
        ('Description','Description.en'),
        ('Description(de)','Description.de'),
        ('Description(fr)','Description.fr'),
        ('Description(it)','Description.it'),
        ('Description(es)','Description.es'),
        ('Description(pl)','Description.pl'),
        ('Description(ch)','Description.ch'),
    
        ('BodyParts','ArticleFamily.body_part'),
        ('News','ArticleFamily.inWebshopNew'),
        ('Sale','ArticleFamily.inWebshopSale'),
        ('InWebshop','ArticleFamily.inWebshop'),
        ('SizeIn','ArticleFamily.measureUnit')])
    
    f = open(tabdelimitedfilename,'r')
    header = [TABXLSMAPPING.get(word, '?%s'%word) for word in f.readline().strip('\n').split('\t')]
    shop = {'shop_ref': shop_ref, 'inWebshop':True, 'name':shop_ref.title(), 'lines' : {}}
    for line in f:
#        print line
        row = dict(
                   [(a,b) for a,b in zip(
                             header, 
                             [(l and (l[0] == '"' and l[-1]== '"' and l[1:-1]) or l).strip('\n').replace('""','"')\
                              for l in line.split('\t')])])

#        pprint.pprint(row)
        shop = updateShopDict(shop, row)    
    
    shop['lines'] = shop['lines'].values()
    for line in shop['lines']:
        for at in line['art_types'].values():
            for af in at['families'].values():
                for a in af['articles'].values():
                    a['options'] = a['options'].values()
                af['articles'] = af['articles'].values()        
            at['families'] = at['families'].values()
        line['art_types'] = line['art_types'].values()

    print 'Data Loaded.', len(shop['lines']), ' Lines'
    deep_import([shop])
    print 'DB Updated'