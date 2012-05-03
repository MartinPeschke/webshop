
delete from apps_profile where user_id = 0;
delete from auth_user_groups;
delete from auth_group;

alter table apps_profile add column is_signup_complete int(1) default 0;


alter table apps_address add column country_iso varchar(2);
alter table apps_address add constraint country_iso FOREIGN KEY (country_iso) references country.iso;
CREATE TABLE `apps_language` (
  `code` varchar(2) NOT NULL,
  `name` varchar(128) NOT NULL,
  `enabled` tinyint(1) NOT NULL default  1,
  PRIMARY KEY (`code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
insert into apps_language (code, name) values ('de', 'Deutsch'), ('en', 'English'), ('fr', 'Français'), ('es', 'Espagnol'), ('it', 'Italiano');
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

