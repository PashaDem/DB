-- name: get_tool_by_name^
SELECT *
FROM tool
WHERE name = :tool_name;

-- name: create_tool!
INSERT INTO tool (name, description, is_deregistered)
VALUES (:name, :description, :is_deregistered);


-- name: get_tool_by_id^
SELECT *
FROM tool
WHERE id = :tool_id;

-- name: update_tool_by_id!
UPDATE tool
SET name            = :name,
    description     = :description,
    is_deregistered = :is_deregistered
WHERE id = :tool_id;

-- name: deregister_tool!
UPDATE tool
SET is_deregistered= TRUE
WHERE id = :tool_id;

-- name: get_tools
SELECT *
FROM tool;

-- name: does_tool_exist^
select *
from tool
where id = :tool_id;