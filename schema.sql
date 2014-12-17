drop table if exists user_details;
create table user_details (
  username text primary key,
  password text not null,
  location text not null,
  gender text not null,
  football text not null default "false",
  basketball text not null default "false",
  tennis text not null default "false",
  badminton text not null default "false",
  cricket text not null default "false"
);

drop table if exists requests;
create table requests (
  request_id integer primary key autoincrement,
  event_id integer default 0,
  requester_user_id text,
  receiver_user_id text,
  location text,
  gender text,
  sport text,
  request_status text
);
