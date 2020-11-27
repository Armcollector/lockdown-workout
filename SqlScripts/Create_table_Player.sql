
drop table  Player

go

create table Player
(
	player_id int IDENTITY not null,
	first_name varchar(50) not null,
	last_name varchar(50) not null,
	nickname varchar(50),
	weight decimal(5,2),
  PRIMARY KEY (first_name,last_name)
)
go

insert into Player (first_name, last_name) values( 'Christian','Sloper')
insert into Player (first_name, last_name) values( 'John Erik','Sloper')


go

select * from Player




