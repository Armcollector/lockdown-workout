select ROW_NUMBER() OVER ( ORDER BY SUM(reps) DESC) AS Plassering, first_name,last_name, SUM(REPS)  from Registration INNER JOIN PLAYER ON Player.player_id = Registration.player_id
        where date_for_pushup = cast(getdate() as date)
        GROUP BY first_name,last_name
        ORDER BY SUM(reps) DESC

select * from Registration

select cast(getdate() as date), getdate(),DATEADD(day,-1,GetDATE())

select ROW_NUMBER() OVER ( ORDER BY SUM(reps) DESC) AS Plassering, first_name,last_name, SUM(REPS)  from Registration INNER JOIN PLAYER ON Player.player_id = Registration.player_id
        where date_for_pushup = dateadd(day,-1,cast(getdate() as date))
        GROUP BY first_name,last_name
        ORDER BY SUM(reps) DESC


select * from player

delete from player where player_id = 11


select * from Registration
order by date_for_pushup desc


with per_day AS (
    SELECT
      player_id,
      date_for_pushup,
      sum(reps) as reps
    FROM Registration
  group by player_id, date_for_pushup
)
select first_name,last_name, max(reps) as max_reps from per_day inner join Player on per_day.player_id = Player.player_id
group by first_name,last_name
order by max(reps) desc


with per_day AS (
        SELECT
          player_id,
          date_for_pushup,
          sum(reps) as reps
        FROM Registration
      group by player_id, date_for_pushup
    )
    select ROW_NUMBER() OVER ( ORDER BY max(reps) DESC) AS Plassering, first_name,last_name, max(reps) as max_reps from per_day inner join Player on per_day.player_id = Player.player_id
    group by first_name,last_name
    order by max(reps) desc

-- activity query

with dates as
(select distinct date_for_pushup from Registration where date_for_pushup >= dateadd(day,-5,cast(getdate() as date))),
  players as
  (select first_name, last_name,player_id from Player where exists(  select 1 from Registration where Player.player_id = Registration.player_id and date_for_pushup >=dateadd(day,-5,cast(getdate() as date)) )),
  reps AS
  (select player_id, date_for_pushup, sum(reps) as reps from Registration
where date_for_pushup >= dateadd(day,-5,cast(getdate() as date))
group by player_id, date_for_pushup)
select dates.date_for_pushup, first_name,last_name, ISNULL(reps,0) reps from dates inner join players on 1 = 1  left OUTER JOIN reps  on reps.player_id = players.player_id and reps.date_for_pushup = dates.date_for_pushup



select player_id, date_for_pushup, sum(reps) from Registration
where date_for_pushup >= dateadd(day,-5,cast(getdate() as date))
group by player_id, date_for_pushup
