CREATE TABLE IF NOT EXISTS credit_info(
    bank_name varchar(30), 
    bank_alias_name text, 
    card_name varchar(30), 
    card_alias_name text,
    card_image text, 
    card_link text, 
    topic text,
    lst_update_dt date,
    PRIMARY KEY (bank_name, card_name)
);