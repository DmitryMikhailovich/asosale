SELECT process_id
       , start_dtm
       , end_dtm
       , status
       , cnt
FROM log_processes
WHERE process_id IN (SELECT MAX(process_id) FROM log_processes);