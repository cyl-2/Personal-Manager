DROP TABLE IF EXISTS users;

CREATE TABLE users 
(
    username TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    code TEXT
);

DROP TABLE IF EXISTS tasks;

CREATE TABLE tasks 
(
    username TEXT NOT NULL,
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    location TEXT,
    task_date DATE NOT NULL
);

DROP TABLE IF EXISTS diary;

CREATE TABLE diary 
(
    username TEXT NOT NULL,
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    entry TEXT NOT NULL,
    weather TEXT,
    date TEXT NOT NULL
);

DROP TABLE IF EXISTS survey;

CREATE TABLE survey
(
    navigation TEXT NOT NULL,
    feature TEXT NOT NULL,
    likeness TEXT NOT NULL,
    occurrence TEXT NOT NULL,
    recommend TEXT NOT NULL
);

DROP TABLE IF EXISTS user_queries;

CREATE TABLE user_queries
(
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    name TEXT NOT NULL,
    message TEXT NOT NULL,
    date DATE NOT NULL
);