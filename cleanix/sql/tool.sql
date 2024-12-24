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
FROM tool where is_deregistered = false;

-- name: does_tool_exist^
select *
from tool
where id = :tool_id;

-- name: get_tools_by_ids
select * from tool where id=any(:tool_ids);

-- name: get_transports_by_ids
select * from transport where id=any(:transport_ids);