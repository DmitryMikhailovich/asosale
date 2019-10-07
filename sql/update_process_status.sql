UPDATE log_processes
SET start_dtm = :start_dtm
, end_dtm = :end_dtm
, status = :status
, cnt = :cnt
WHERE process_id = :process_id;