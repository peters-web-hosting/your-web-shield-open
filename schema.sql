DROP DATABASE IF EXISTS public;
CREATE DATABASE IF NOT EXISTS public;
USE public;

CREATE TABLE asnrisk (
  asn STRING(45) NOT NULL,
  asnname STRING(255) NULL,
  risk FLOAT8 NULL,
  CONSTRAINT asnrisk_pkey PRIMARY KEY (asn ASC)
);

CREATE TABLE bots (
  ip STRING(255) NOT NULL,
  botname STRING(255) NULL,
  typeofbot INT8 NULL,
  CONSTRAINT bots_pkey PRIMARY KEY (ip ASC)
);

CREATE TABLE codes (
  httpcode INT8 NOT NULL,
  risk FLOAT8 NULL,
  CONSTRAINT codes_pkey PRIMARY KEY (httpcode ASC)
);

CREATE TABLE countryrisk (
  id STRING(2) NOT NULL,
  risk FLOAT8 NULL,
  name VARCHAR(255) NULL,
  CONSTRAINT countryrisk_pkey PRIMARY KEY (id ASC)
);

CREATE TABLE requestrisk (
  request STRING(255) NOT NULL,
  risk FLOAT8 NULL,
  CONSTRAINT requestrisk_pkey PRIMARY KEY (request ASC)
);

CREATE TABLE iplog (
  id INT8 NOT NULL DEFAULT unique_rowid(),
  ip VARCHAR(256) NULL,
  risk FLOAT8 NULL,
  datereported DATE NULL,
  country VARCHAR(255) NULL,
  asn VARCHAR(255) NULL,
  CONSTRAINT iplog_pkey PRIMARY KEY (id ASC),
  INDEX iplog_country_idx (country ASC) STORING (risk),
  INDEX iplog_asn_idx (asn ASC) STORING (risk)
);



CREATE TABLE ratelimit (
  id INT8 NOT NULL DEFAULT unique_rowid(),
  ip VARCHAR(255) NULL,
  expires TIMESTAMP NULL,
  rowid INT8 NOT VISIBLE NOT NULL DEFAULT unique_rowid(),
  CONSTRAINT ratelimit_pkey PRIMARY KEY (rowid ASC)
);

CREATE TABLE user_reports (
  rowid INT8 NOT NULL DEFAULT unique_rowid(),
  ip STRING(256) NULL,
  date TIMESTAMP NULL,
  CONSTRAINT user_reports_pkey PRIMARY KEY (rowid ASC)
);

CREATE TABLE users (
  id INT8 NOT NULL DEFAULT unique_rowid(),
  username VARCHAR(20) NOT NULL,
  email VARCHAR(120) NOT NULL,
  workos_id VARCHAR(50) NULL,
  is_subscribed BOOL NULL DEFAULT false,
  stripe_customer_id VARCHAR(50) NULL,
  stripe_subscription_id VARCHAR(50) NULL,
  confirmed BOOL NULL DEFAULT false,
  "role" VARCHAR(50) NOT NULL DEFAULT 'user':::STRING,
  CONSTRAINT users_pkey PRIMARY KEY (id ASC),
  UNIQUE INDEX users_username_key (username ASC),
  UNIQUE INDEX users_email_key (email ASC)
);

CREATE TABLE user_tracked_ips (
  id INT8 NOT NULL DEFAULT unique_rowid(),
  address VARCHAR(100) NOT NULL,
  user_id INT8 NOT NULL,
  CONSTRAINT user_tracked_ips_pkey PRIMARY KEY (id ASC),
  CONSTRAINT user_tracked_ips_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE wplog (
  id INT8 NOT NULL DEFAULT unique_rowid(),
  ip VARCHAR(256) NULL,
  date TIMESTAMP NULL DEFAULT current_timestamp():::TIMESTAMP,
  risk FLOAT8 NULL,
  CONSTRAINT wplog_pkey PRIMARY KEY (id ASC)
);

CREATE TABLE user_report (
  id STRING(64) NOT NULL UNIQUE,
  user_id VARCHAR(256) NOT NULL,
  status INT8 NOT NULL DEFAULT 0,
  first_date_in_log STRING(255) NULL,
  last_date_in_log STRING(255) NULL,
  date_uploaded TIMESTAMP NULL DEFAULT current_timestamp():::TIMESTAMP,
  date_completed TIMESTAMP NULL,
  CONSTRAINT user_report_pkey PRIMARY KEY (id ASC)
);

CREATE TABLE report_row (
  report_id STRING(64) NOT NULL,
  ip VARCHAR(256) NOT NULL,
  risk FLOAT8 NULL,
  occurrences FLOAT8 NULL,
  asn STRING NULL,
  asnname STRING(255) NULL,
  country STRING(255)  NULL,
  CONSTRAINT user_report_row_pkey PRIMARY KEY (report_id ASC, ip ASC),
  CONSTRAINT user_report_row_report_id_fkey FOREIGN KEY (report_id) REFERENCES user_report(id) ON DELETE CASCADE
);