--- Init the database. Use the - 5 times to separate statements
DROP TABLE IF EXISTS test_table;
-----
CREATE TABLE IF NOT EXISTS test_table (
	id integer PRIMARY KEY AUTOINCREMENT,
	description VARCHAR(255),
	date TIMESTAMP
);
-----
INSERT INTO test_table (description, date) VALUES (
  'test',
  '2016-06-22 19:10:25-07'
);
-----
INSERT INTO test_table (description, date) VALUES (
  'test2',
  'big fest'
);