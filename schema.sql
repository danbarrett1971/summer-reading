drop table if exists books;
create table books (
  id integer primary key autoincrement,
  username text,
  author text,
  title text not null,
  description text not null,
  rating text  
);

drop table if exists users;
create table users ( 
   id integer primary key autoincrement,
   name text not null,
   nickname text not null,
   email text 
   password text not null,
   full_librarycard text,
);
 
