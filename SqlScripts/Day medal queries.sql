select T.*
from
  (
  SELECT
    date_for_pushup,
    player_id,
    sum(reps) as sum_reps,
    rank()
    OVER ( PARTITION BY date_for_pushup
      ORDER BY sum(reps) DESC ) as rnk
  FROM Registration
  GROUP BY date_for_pushup, player_id
) T
where T.rnk = 1
  and date_for_pushup <>cast(getdate() as date)


select T.player_id, count(*)
from
  (
  SELECT
    date_for_pushup,
    player_id,
    sum(reps) as sum_reps,
    rank()
    OVER ( PARTITION BY date_for_pushup
      ORDER BY sum(reps) DESC ) as rnk
  FROM Registration
  GROUP BY date_for_pushup, player_id
) T
where T.rnk = 1
  and date_for_pushup <>cast(getdate() as date)
group by player_id

select T.player_id, T.first_name, T.last_name, sum(case when rnk = 1 then 1 else 0 end ) as gold, sum(case when rnk = 2 then 1 else 0 end ) as silver, sum(case when rnk = 3 then 1 else 0 end ) as bronze
from
  (
          SELECT
    first_name,
    last_name,
    date_for_pushup,
    Player.player_id,
    sum(reps) as sum_reps,
    rank()
            OVER ( PARTITION BY date_for_pushup
              ORDER BY sum(reps) DESC ) as rnk
  FROM Registration inner join Player on Registration.player_id = Player.player_id
  GROUP BY first_name,last_name,date_for_pushup, Player.player_id
        ) T
where T.rnk <= 3
  and date_for_pushup <>cast(getdate() as date)
group by first_name,last_name,player_id
order by count(*) desc


-- query to get max of each
select player_id , [0] as [Sit ups], [1] as [Air Squats], [2] as [Push ups], [3] as [Pull ups]
from
  (  select player_id, exercise_id, reps
  from Registration ) AS sourceTable
PIVOT
(
    sum(reps)
    for exercise_id in ( [0],[1],[2],[3] )
) AS PivotTable
