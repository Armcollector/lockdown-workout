create table Challenge
(
	challenge_id int not null
		primary key,
	challenge_navn varchar(50),
	challenge_description varchar(300),
	exercise_type_id int
)
go

create table Exercise
(
	exercise_type_id int,
	exercise_name varchar(50),
	exercise_description varchar(300)
)
go


drop table if exists Registration
go

create table Registration
(
	reg_id int identity,
	exercise_id int,
	player_id int,
	reps int,
	dt date
		primary key (exercise_id, player_id, dt)
)
go

drop table if exists Pushupchallenge_user
GO


create table Pushupchallenge_user
(
	id int identity
		primary key nonclustered,
	username varchar(120),
	email varchar(120),
	password_hash varchar(128)
)
go