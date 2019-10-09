SELECT coalesce(strftime('%s', 'now') - MIN(lastmod) > 7 * 24 * 60 * 60, 1) AS NEED_TO_UPDATE
FROM web_categories
;