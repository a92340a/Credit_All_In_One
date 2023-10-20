CREATE TABLE IF NOT EXISTS card_dict(
    card_no serial NOT NULL,
    card_name varchar(30) NOT NULL, 
    card_alias_name text,
    lst_mtn_dt date
);