-- name: insert_feedback!
INSERT INTO feedback (create_at, score, description, client_id)
VALUES (:create_at, :score, :description, :client_id);

-- name: get_feedback_by_client_id^
SELECT *
FROM feedback
where client_id = :client_id;

-- name: update_feedback_by_id!
UPDATE feedback
SET score       = :score,
    description = :description
WHERE id = :id;

-- name: delete_feedback_by_client_id!
DELETE
FROM feedback
WHERE client_id = :client_id;


-- name: get_feedbacks
SELECT *
FROM feedback;

-- name: get_feedback_by_id^
SELECT * FROM feedback WHERE id = :feedback_id;