--- Init the database. Use the - 5 times to separate statements
DROP TABLE IF EXISTS command_list
-----
CREATE TABLE IF NOT EXISTS log_message (
	id_message INTEGER,
	chat_id INTEGER,
	username VARCHAR(255),
	name VARCHAR(255),
	surname VARCHAR(255),
	text VARCHAR(255),
	date DATE,
	PRIMARY KEY (id_message,chat_id,date)
);
-----
CREATE TABLE IF NOT EXISTS command_list (
	commnad_id SERIAL PRIMARY KEY ,
	name VARCHAR(255),
	description VARCHAR(255)
);
