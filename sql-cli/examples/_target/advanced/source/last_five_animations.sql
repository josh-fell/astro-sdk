SELECT *
FROM {{source__imdb_movies}}
WHERE genre1='Animation'
ORDER BY rating asc
LIMIT 5;