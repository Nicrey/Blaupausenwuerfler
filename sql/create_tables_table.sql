CREATE TABLE IF NOT EXISTS roll_tables_next (
  table_name varchar(255) PRIMARY KEY,
  table_category varchar(255) NOT NULL,
  table_json JSON NOT NULL,
  table_type varchar(255) NOT NULL
);
