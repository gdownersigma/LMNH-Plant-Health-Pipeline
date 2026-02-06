SELECT
    p.plant_id,
    p.name AS plant_name,
    b.botanist_id,
    b.name AS botanist_name,
    cn.country_id,
    cn.country_name
FROM plant AS p 
JOIN botanist AS b
    ON p.botanist_id = b.botanist_id
JOIN origin AS o
    ON p.origin_id = o.origin_id
JOIN city AS c
    ON o.city_id = c.city_id
JOIN country AS cn
    ON c.country_id = cn.country_id
ORDER BY p.plant_id;