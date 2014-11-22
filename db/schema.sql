
drop table if exists books;
CREATE TABLE books (
  id integer primary key autoincrement,
  userid integer not null, 
  title varchar(50) not null,
  author varchar(50),
  description text,
  rating varchar(1));

drop table if exists users;
CREATE TABLE users ( 
   id integer primary key autoincrement,
   nickname varchar(20) not null,
   password varchar(20) not null,
   fullname varchar(50),
   full_librarycard varchar(20),
   email varchar(50),
   registered_on datetime
   );
