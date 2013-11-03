mysqldump -uper4 -pAster74IX devel apps_shop apps_line apps_articletype apps_articlefamily apps_article apps_articleoption apps_pricing apps_languagepack apps_promotion > 20081023_updated_dump.sql

mysqldump -uper4 -pAster74IX devel auth_user apps_profile apps_address > 20090202_profiles.sql


mysql -uper4 -pAster74IX -e "source 20090213_webdb_baseline_l.sql" devel --default_character_set utf8

rm -rf `find . -type d -name .svn`
