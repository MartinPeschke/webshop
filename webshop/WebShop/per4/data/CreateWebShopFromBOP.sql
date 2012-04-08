#Delete empty articles
delete a, p from article a left outer join articleoption ao on ao.a_id = a.id left outer join a_pricing p on p.a_id = a.id  where ao.id is NULL;
#delete empty families
delete af from articlefamily af left outer join article a on a.articlefamily_id = af.id where a.id is NULL;
#delete empty types
delete at from articletype at left outer join articlefamily af on af.at_id = at.id where af.id is NULL;
#delete empty lines
delete line from line left outer join articlefamily af on af.line_id = line.id where af.id is NULL;

DROP TABLE IF EXISTS `apps_shop`;
CREATE TABLE `apps_shop` (
  `id` int(11) NOT NULL auto_increment,
  `ref` varchar(48) NOT NULL default '',
  `logopath` varchar(128) default NULL,
  `viewableByRole` char(2) default NULL,
  `sort` int(11) default 0,
  `name_I18N_id` int(11) NOT NULL default '0',
  `newTemplate` varchar(128) default NULL,
  `saleTemplate` varchar(128) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `ref` (`ref`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

insert into apps_shop
	(select id, shop_ref, logopath, webshop_viewableByRole, 0, name_I18N_id, NULL, NULL from shop where inWebshop = 1);


update apps_shop set sort = 0 where ref = 'piercing';
update apps_shop set sort = 1 where ref = 'tattoo';
update apps_shop set sort = 3 where ref = 'fashion_-_media';
update apps_shop set sort = 2 where ref = 'jewellery';
update apps_shop set sort = 4 where ref = 'studio_equipment';

DROP TABLE IF EXISTS `apps_languagepack`;
CREATE TABLE `apps_languagepack` (
  `id` int(11) NOT NULL auto_increment,
  `message_id` varchar(48) default NULL,
  `en` varchar(255) NOT NULL default '',
  `de` varchar(255) default NULL,
  `fr` varchar(255) default NULL,
  `it` varchar(255) default NULL,
  `pl` varchar(255) default NULL,
  `es` varchar(255) default NULL,
  `dk` varchar(255) default NULL,
  `sw` varchar(255) default NULL,
  `no` varchar(255) default NULL,
  `ru` varchar(255) default NULL,
  `gr` varchar(255) default NULL,
  `nl` varchar(255) default NULL,
  `ch` varchar(255) default NULL,
  `create_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `update_time` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2038 DEFAULT CHARSET=latin1;

insert into apps_languagepack select *, NULL, NULL from languagepack;

DROP TABLE IF EXISTS `apps_line`;
CREATE TABLE `apps_line` (
  `id` int(11) NOT NULL auto_increment,
  `ref` varchar(48) NOT NULL default '',
  `logopath` varchar(128) default NULL,
  `sort` int(11) default 0,
  `viewableByRole` char(2) default NULL,
  `shop_id` int(11) NOT NULL default '0',
  `name_I18N_id` int(11) default NULL,
  `template_path` varchar(64) default 'line.html',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `ref` (`ref`),
  KEY `apps_line_shop_id` (`shop_id`)
) ENGINE=MyISAM AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;

insert into apps_line
	(select id, line_ref, logopath, sortPosition, webshop_viewableByRole, shop_id, name_I18N_id, NULL from line where inWebshop = 1);


insert into apps_languagepack values (null, 'Line.name', 'NEW', 'NEU', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'piercing_new', 'new.jpg', -1, null, 44 , last_insert_id(), 'line_new.html');

insert into apps_languagepack values (null, 'Line.name', 'SALE', 'ANGEBOTE', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'piercing_sale', 'sale_{{LOCALE}}.jpg', 30, null, 44, last_insert_id(), 'line_sale.html');

insert into apps_languagepack values (null, 'Line.name', 'NEW', 'NEU', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'tattoo_new', 'new.jpg', -1, null, 43, last_insert_id(), 'line_new.html');

insert into apps_languagepack values (null, 'Line.name', 'SALE', 'ANGEBOTE', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'tattoo_sale', 'sale_{{LOCALE}}.jpg', 30, null, 43, last_insert_id(), 'line_sale.html');

insert into apps_languagepack values (null, 'Line.name', 'NEW', 'NEU', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'jewellery_new', 'new.jpg', -1, null, 47 , last_insert_id(), 'line_new.html');

insert into apps_languagepack values (null, 'Line.name', 'SALE', 'ANGEBOTE', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'jewellery_sale', 'sale_{{LOCALE}}.jpg', 30, null, 47, last_insert_id(), 'line_sale.html');

insert into apps_languagepack values (null, 'Line.name', 'NEW', 'NEU', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'fashion_new', 'new.jpg', -1, null, 46, last_insert_id(), 'line_new.html');

insert into apps_languagepack values (null, 'Line.name', 'SALE', 'ANGEBOTE', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'fashion_sale', 'sale_{{LOCALE}}.jpg', 30, null, 46, last_insert_id(), 'line_sale.html');

insert into apps_languagepack values (null, 'Line.name', 'NEW', 'NEU', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'studio_new', 'new.jpg', -1, null, 45, last_insert_id(), 'line_new.html');

insert into apps_languagepack values (null, 'Line.name', 'SALE', 'ANGEBOTE', '', '', '', '', '', '', '', '', '', '', '', NOW(), NOW());
insert into apps_line values (null, 'studio_sale', 'sale_{{LOCALE}}.jpg',  30, null, 45, last_insert_id(), 'line_sale.html');




DROP TABLE IF EXISTS `apps_articletype`;
CREATE TABLE `apps_articletype` (
  `id` int(11) NOT NULL auto_increment,
  `line_id` int(11) NOT NULL default '0',
  `en` varchar(255) NOT NULL default '',
  `de` varchar(255) default NULL,
  `fr` varchar(255) default NULL,
  `it` varchar(255) default NULL,
  `pl` varchar(255) default NULL,
  `es` varchar(255) default NULL,
  `dk` varchar(255) default NULL,
  `sw` varchar(255) default NULL,
  `no` varchar(255) default NULL,
  `ru` varchar(255) default NULL,
  `gr` varchar(255) default NULL,
  `nl` varchar(255) default NULL,
  `ch` varchar(255) default NULL,
  `create_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `update_time` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`id`),
  KEY `apps_articletype_line_id` (`line_id`)
) ENGINE=MyISAM AUTO_INCREMENT=183 DEFAULT CHARSET=latin1;

insert into apps_articletype
	select *, NULL, NULL from articletype;
	
DROP TABLE IF EXISTS `apps_articlefamily`;
CREATE TABLE `apps_articlefamily` (
  `id` int(11) NOT NULL auto_increment,
  `ref` varchar(64) NOT NULL default '',
  `logopath` varchar(128) default NULL,
  `create_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `update_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `desc_I18N_id` int(11) default NULL,
  `body_part` varchar(255) default NULL,
  `shop_new` tinyint(1) default NULL,
  `line_id` int(11) NOT NULL default '0',
  `art_type_id` int(11) NOT NULL default '0',
  `shop_sale` tinyint(1) default NULL,
  `shop_newprice` tinyint(1) default NULL,
  `shop_newsize` tinyint(1) default NULL,
  `min_price_e` decimal(10,2) default NULL,
  `min_price_K` decimal(10,2) default NULL,
  `has_more_E` tinyint(1) default NULL,
  `has_more_K` tinyint(1) default NULL,       
  PRIMARY KEY  (`id`),
  UNIQUE KEY `ref` (`ref`),
  KEY `apps_articlefamily_line_id` (`line_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1918 DEFAULT CHARSET=latin1;

insert into apps_articlefamily
	(select id, af_ref, logopath, created, NOW(), desc_I18N_id, body_part, inWebshopNew, line_id, at_id, inWebshopSale, inWebshopNewPrice, inWebshopNewSize, NULL, NULL, NULL, NULL
	from articlefamily where inWebshop = 1);

DROP TABLE IF EXISTS `apps_article`;
CREATE TABLE `apps_article` (
  `id` int(11) NOT NULL auto_increment,
  `ref` varchar(255) NOT NULL default '',
  `create_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `update_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `diameter_length` double default NULL,
  `ball_size1` double default NULL,
  `ball_size2` double default NULL,
  `thickness` double default NULL,
  `measure` varchar(4) default NULL,
  `packaging_unit` int(11) default NULL,
  `weight` double default NULL,
  `article_family_id` int(11) NOT NULL default '0', 
  PRIMARY KEY  (`id`),
  UNIQUE KEY `ref` (`ref`),
  KEY `apps_article_article_family_id` (`article_family_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5941 DEFAULT CHARSET=latin1;

insert into apps_article
	(select a.id, a.a_ref, a.created, NOW(), 
	a.diameter_len, a.ball_size1, a.ball_size2, a.thickness, a.measure_unit, a.packaging_unit, a.weight, 
	a.articlefamily_id from article a join articlefamily af on a.articlefamily_id = af.id where af.inWebshop = 1);

 
DROP TABLE IF EXISTS `apps_articleoption`;
CREATE TABLE `apps_articleoption` (
  `id` int(11) NOT NULL auto_increment,
  `ref` varchar(16) NOT NULL default '',
  `quantity_stock` int(11) default NULL,
  `sub_image_code` varchar(48) default NULL,
  `article_id` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  KEY `apps_articleoption_article_id` (`article_id`)
) ENGINE=MyISAM AUTO_INCREMENT=16013 DEFAULT CHARSET=latin1;
 
 
 insert into apps_articleoption
 	(select ao.id, ao.ao_ref, 0, ao.subImgCode, a_id from articleoption ao join article a on ao.a_id = a.id join articlefamily af on af.id = a.articlefamily_id where af.inWebshop = 1);
 	

DROP TABLE IF EXISTS `apps_pricing`;
CREATE TABLE `apps_pricing` (
  `id` int(11) NOT NULL auto_increment,
  `_price` double NOT NULL default '0',
  `discountQty` int(11) default NULL,
  `forRole` char(1) NOT NULL default '',
  `create_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `update_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `article_id` int(11) NOT NULL default '0',
  `for_promotion` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `apps_pricing_article_id` (`article_id`)
) ENGINE=MyISAM AUTO_INCREMENT=29607 DEFAULT CHARSET=latin1;

 
 insert into apps_pricing
 	(select p.id, p.price, p.discountQty, p.cg_ref, NOW(), NOW(), p.a_id, 0 from a_pricing p join article a on p.a_id = a.id join articlefamily af on af.id = a.articlefamily_id where af.inWebshop = 1 and price != 0.0);
 
 update apps_pricing set _price = Round(FLOOR(_price * 119)/100, 2) where forRole = 'E';
 
 drop table if exists tmp;
 create temporary table tmp (
 	af_ref varchar(64) DEFAULT NULL,
 	min_price DECIMAL(10,2),
 	has_more TINYINT(1),
 	role varchar(1)
 );
 insert into tmp (af_ref, role, min_price, has_more) (select af.ref, p.forRole, min(p._price), min(p._price) != max(p._price) from apps_articlefamily af left outer join apps_article a on a.article_family_id = af.id left outer join apps_pricing p on p.article_id = a.id group by af.ref, p.forRole);
 update apps_articlefamily, tmp set min_price_E = min_price, has_more_E = has_more where tmp.af_ref = apps_articlefamily.ref and role='E';
 update apps_articlefamily, tmp set min_price_K = min_price, has_more_K = has_more where tmp.af_ref = apps_articlefamily.ref and role='K';

 
#Remove NA Articles
#delete apps_articlefamily, apps_article, apps_articleoption, apps_pricing, apps_promotion 	
#	from apps_articlefamily 
#	left outer join apps_article on apps_articlefamily.id = apps_article.article_family_id 
#	left outer join apps_articleoption on apps_article.id = apps_articleoption.article_id 
#	left outer join apps_pricing on apps_article.id = apps_pricing.article_id
#	left outer join apps_promotion on apps_articlefamily.id = apps_promotion.family_id
#	where apps_articlefamily.ref like 'NA%';
#	
#Remove all Old OFFs
#delete apps_articlefamily, apps_article, apps_articleoption, apps_pricing, apps_promotion 	
#	from apps_articlefamily 
#	left outer join apps_article on apps_articlefamily.id = apps_article.article_family_id 
#	left outer join apps_articleoption on apps_article.id = apps_articleoption.article_id 
#	left outer join apps_pricing on apps_article.id = apps_pricing.article_id
#	left outer join apps_promotion on apps_articlefamily.id = apps_promotion.family_id
#	where apps_articlefamily.ref like 'OFF%';	
	
 	
DROP TABLE IF EXISTS `apps_promotion`;
CREATE TABLE `apps_promotion` (
  `id` int(11) NOT NULL auto_increment,
  `family_id` int(11) NOT NULL default '0',
  `shop_id` int(11) NOT NULL default '0',
  `desc_I18N_id` int(11) default NULL,
  `logopath` varchar(128) default NULL,
  `create_time` datetime default NULL,
  `update_time` datetime default NULL,
  `start_time` datetime default NULL,
  `end_time` datetime default NULL,
  `is_sale` tinyint(1) default NULL,
  `is_new` tinyint(1) default NULL,
  `is_newprice` tinyint(1) default NULL,
  `is_newsize` tinyint(1) default NULL,
  `is_active` tinyint(1) default '1',
  PRIMARY KEY  (`id`),
  KEY `apps_promotion_family_id` (`family_id`),
  KEY `apps_promotion_shop_id` (`shop_id`)
) ENGINE=MyISAM AUTO_INCREMENT=153 DEFAULT CHARSET=latin1;


insert into apps_promotion
	(select NULL, af.id, shop_id, af.desc_I18N_id, af.logopath, NOW(), NOW(), NOW(), "0000-00-00", 
	af.inWebshopSale, af.inWebshopNew, af.inWebshopNewPrice, af.inWebshopNewSize, 1 
	from articlefamily af join line on line.id = af.line_id 
	where af.inWebshopSale
	or (inWebshopNew and af.created >= date_sub(now(), interval 1 month))
	or af.inWebshopNewPrice 
	or af.inWebshopNewSize);
	
	
	
#delete empty types Shop
delete at from apps_articletype at left outer join apps_articlefamily af on af.art_type_id = at.id where af.id is NULL;