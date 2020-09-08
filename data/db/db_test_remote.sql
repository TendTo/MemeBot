--- Init the database. Use the - 5 times to separate statements
DROP TABLE IF EXISTS test_table;
-----
CREATE TABLE IF NOT EXISTS test_table (
	id  SERIAL PRIMARY KEY,
	description VARCHAR(255),
	date TIMESTAMP
);
-----
INSERT INTO test_table (description, date) VALUES (
  'test',
  '2016-06-22 19:10:25'
);
-----
INSERT INTO test_table (description, date) VALUES (
  'test2',
  '2020-06-22 19:10:25'
);