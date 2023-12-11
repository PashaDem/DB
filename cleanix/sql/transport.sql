-- name: get_transport_by_name^
SELECT *
FROM transport
WHERE name = :transport_name;

-- name: create_transport!
INSERT INTO transport (name, description, is_deregistered, brand)
VALUES (:name, :description, :is_deregistered, :brand);


-- name: get_transport_by_id^
SELECT *
FROM transport
WHERE id = :transport_id;

-- name: update_transport_by_id!
UPDATE transport
SET name            = :name,
    description     = :description,
    is_deregistered = :is_deregistered,
    brand           = :brand
WHERE id = :transport_id;

-- name: deregister_transport!
UPDATE transport
SET is_deregistered= TRUE
WHERE id = :transport_id;

-- name: get_transports
SELECT *
FROM transport;

-- name: does_transport_exist^
SELECT *
FROM transport
where id = :transport_id;