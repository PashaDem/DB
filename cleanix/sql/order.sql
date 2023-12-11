-- name: insert_full_order^
select insert_full_order(:address, :clean_date, :client_id, :status);


-- name: get_order_by_id^
select *
from cleaning_order
where id = :order_id;

-- name: get_orders_by_user_id
select *
from cleaning_order
where client_id = :user_id;

-- name: delete_order_by_id!
DELETE
FROM cleaning_order
WHERE id = :order_id;

-- name: append_services_to_order!
CALL append_new_service(:services, :order_id);

-- name: remove_service_from_order!
DELETE
FROM public.order_to_service
WHERE service_id = :service_id
  AND order_id = :order_id;

-- name: assign_order_by_employee_id!
INSERT INTO public.order_to_employee (order_id, employee_id)
VALUES (:order_id, :employee_id);

-- name: get_order_employees_by_order_id
select employee_id
from public.order_to_employee
where order_id = :order_id;

-- name: mark_order_as_in_process_by_order_id!
update cleaning_order
set status = 'INPROCESS'
where id = :order_id;

-- name: mark_order_as_paid_by_order_id!
update cleaning_order
set status = 'PAID'
where id = :order_id;

-- name: get_all_order_transports
select transport_id
from order_to_transport
where order_id = :order_id;

-- name: insert_transport_to_order!
insert into order_to_transport (order_id, transport_id)
values (:order_id, :transport_id);

-- name: remove_transport_from_order!
delete
from order_to_transport
where order_id = :order_id
  and transport_id = :transport_id;

-- name: get_all_order_tools
select tool_id
from order_to_tool
where order_id = :order_id;

-- name: insert_tool_to_order!
insert into order_to_tool (order_id, tool_id)
values (:order_id, :tool_id);

-- name: remove_tool_from_order!
delete
from order_to_tool
where order_id = :order_id
  and tool_id = :tool_id;