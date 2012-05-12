delete from apps_profile where user_id = 0;
delete from auth_user_groups;
delete from auth_group;

alter table country add column is_default tinyint(1) default 0;
update country set is_default = 1 where iso = 'DE';

alter table apps_address add column country_iso varchar(2);
alter table apps_address add constraint country_iso FOREIGN KEY (country_iso) references country.iso;
CREATE TABLE `apps_language` (
  `code` varchar(2) NOT NULL,
  `name` varchar(128) NOT NULL,
  `enabled` tinyint(1) NOT NULL default 1,
  `is_default` tinyint(1) NOT NULL default 0,
  PRIMARY KEY (`code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
insert into apps_language (code, name) values ('de', 'Deutsch'), ('en', 'English'), ('fr', 'Français'), ('es', 'Espagnol'), ('it', 'Italiano');
update apps_language set is_default = 1 where code = 'de';

alter table apps_address add column language_code varchar(2);
alter table apps_address add constraint language_code FOREIGN KEY (language_code) references apps_language.code;


CREATE TABLE `apps_address_type` (
  `id` integer auto_increment NOT NULL,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
insert into apps_address_type values (1, 'billing'), (2, 'shipping');


CREATE TABLE `apps_address_type` (
  `id` integer auto_increment NOT NULL,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
ALTER TABLE apps_address_type ADD UNIQUE (name);

insert into apps_address_type values (1, 'billing'), (2, 'shipping');

alter table apps_address add column address_type int(11);
alter table apps_address add constraint address_type FOREIGN KEY (address_type) references apps_address_type.id;
update apps_address set address_type = 1 where type = 'billing';
update apps_address set address_type = 2 where type = 'shipping';
alter table apps_address drop column type;
alter table apps_address change address_type `type_id` int(11);


alter table apps_address change country country_legacy varchar(32);
alter table apps_address change country_iso country_id varchar(2);

alter table apps_address change `language` language_legacy varchar(32);
alter table apps_address change language_code `language_id` varchar(2);


update apps_profile set weekdays = REPLACE(weekdays, "'", '"');


-- ORDER STATUS

CREATE TABLE `apps_order_status` (
  `id` integer NOT NULL,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
insert into apps_order_status values (-2, 'ERROR'), (-1, 'DELETED'), (0, 'CURRENT'), (1, 'ORDERED'), (2, 'SUBMITTED_TO_BACKEND');
alter table apps_order change status `status_id` int not null;
alter table apps_order add constraint status_id FOREIGN KEY (status_id) references apps_order_status.id;

-- PAYMENT METHODS

CREATE TABLE apps_payment_method (
  `id` integer NOT NULL,
  `name` varchar(128) NOT NULL UNIQUE,
  `least_role` char(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
insert into apps_payment_method values (1, 'CASH', 'E'), (2, 'CASH_ON_DELIVERY', 'E'), (3, 'BANK_TRANSFER', 'E'), (4, 'CREDITCARD', 'E'), (5, 'DIRECT_DEBIT', 'K'), (6, 'PAYPAL', 'X');

alter table apps_order add column payment_method_id int(11);
alter table apps_order add constraint payment_method_id FOREIGN KEY (payment_method_id) references apps_payment_method.id;


-- CREDIT CARD TYPES

CREATE TABLE apps_creditcard_type (
  `id` integer NOT NULL,
  `name` varchar(128) NOT NULL UNIQUE,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
insert into apps_creditcard_type values (1, 'VISA'), (2, 'MASTERCARD');

alter table apps_creditcard add column cctype_id int(11) not null;
update apps_creditcard set cctype_id = 1 where ctype = 'V';
update apps_creditcard set cctype_id = 2 where ctype = 'M';
alter table apps_creditcard add constraint cctype_id FOREIGN KEY (cctype_id) references apps_creditcard_type.id;
alter table apps_creditcard drop column ctype;


--  ADD PREFERRED PAYMENT METHOD ID
alter table apps_profile add column preferred_payment_method_id int(11);
update apps_profile set preferred_payment_method_id = 1 where payment_method = 'CASH';
update apps_profile set preferred_payment_method_id = 2 where payment_method = 'COD';
update apps_profile set preferred_payment_method_id = 3 where payment_method = 'Transfer';
update apps_profile set preferred_payment_method_id = 4 where payment_method = 'Credit';
update apps_profile set preferred_payment_method_id = 5 where payment_method = 'Direct';
update apps_profile set preferred_payment_method_id = 6 where payment_method = 'Paypal';
alter table apps_profile add constraint preferred_payment_method_id FOREIGN KEY (preferred_payment_method_id) references apps_payment_method.id;
alter table apps_profile drop column payment_method;
