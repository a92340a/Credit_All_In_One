CREATE TABLE IF NOT EXISTS question_answer(
    q_id serial NOT NULL,
    create_dt date,
    create_timestamp int,
    question text, 
    answer text, 
    keyword1 varchar(20), 
    keyword2 varchar(20), 
    keyword3 varchar(20), 
    topic text
);