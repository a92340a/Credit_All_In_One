CREATE TABLE IF NOT EXISTS card_dictionary(
    card_no serial NOT NULL,
    card_name varchar(50) NOT NULL, 
    card_alias_name text,
    lst_mtn_dt date,
    PRIMARY KEY (card_name)
);