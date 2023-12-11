-- name: get_service_by_id^
SELECT *
FROM service
WHERE id = :service_id;

-- name: create_service!
INSERT INTO service (type, description, price, is_archived, name)
VALUES (:type, :description, :price, :is_archived, :name);

-- name: get_service_by_name^
SELECT *
FROM service
WHERE name = :service_name;

-- name: update_service_by_id!
UPDATE service
SET type        = :type,
    name        = :name,
    description = :description,
    price       = :price,
    is_archived = :is_archived
WHERE id = :service_id;

-- name: archive_service_by_id!
UPDATE service
SET is_archived = TRUE
WHERE id = :service_id;

-- name: get_services
SELECT *
FROM service;