
delete from apps_profile where user_id = 0;
delete from auth_user_groups;
delete from auth_group;

alter table apps_profile add column is_signup_complete int(1) default 0;



