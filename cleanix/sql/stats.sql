-- name: increment_order_count!
call increment_order_count(:statistics_id);


-- name: decrement_orders_count!
call decrement_orders_count(:client_id);

-- name: update_total_cost_by_order_id!
call update_total_cost_by_order_id(:order_id);

-- name: mark_feedback_as_left!
update statistics set left_feedback = TRUE where id = :statistics_id;

-- name: mark_feedback_as_deleted!
update statistics set left_feedback = FALSE where id = :statistics_id;