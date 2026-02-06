SELECT
    pr.plant_id,
    p.name AS plant_name,
    pr.soil_moisture,
    pr.temperature,
    pr.last_watered,
    pr.recording_taken,
    p.image_url
FROM plant_reading AS pr
JOIN plant AS p 
    ON pr.plant_id = p.plant_id
WHERE recording_taken > DATEADD(hour, -24, GETDATE());