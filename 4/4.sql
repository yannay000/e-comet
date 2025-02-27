SELECT
    phrase,
    arrayMap(hour ->
        (hour,
         maxIf(views, toHour(dt) = hour) - maxIf(views, toHour(dt) = hour - 1)
        ),
    range(0, 24)) AS views_by_hour
FROM
    phrases_views
WHERE
    campaign_id = 1111111 AND
    toDate(dt) = today()
GROUP BY
    phrase
ORDER BY
    phrase;
