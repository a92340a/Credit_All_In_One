CREATE TABLE IF NOT EXISTS question_answer(
    q_id serial NOT NULL,
    sid varchar(20),
    create_dt date,
    create_timestamp int,
    question text, 
    answer text,
    user_icon text
);