drop table if exists user_details;
create table user_details (
  user_email text primary key,
  password text not null,
  location text not null,
  gender text not null,
  football boolean not null,
  basketball boolean not null,
  tennis boolean not null,
  badminton boolean not null,
  cricket boolean not null
);

drop table if exists requests;
create table requests (
  request_id integer primary key autoincrement,
  event_id integer not null,
  requester_user_id text not null,
  receiver_user_id text not null,
  location text not null,
  gender text not null,
  sport text not null,
  request_status text not null
);