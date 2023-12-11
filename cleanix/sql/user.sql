-- name: get_user_by_username^
select *
from public.user
where username = :username;

-- name: get_user_by_id^
select *
from public.user
where id = :user_id;


-- name: update_password!
update public.user
set password = :new_password
where id = :user_id;

-- name: get_employee_by_user_id^
select *
from public.employee
where id = :user_id;

-- name: get_client_by_user_id^
select *
from public.client
where id = :user_id;

-- name: get_employee_by_username^
select usr.username, usr.fullname, usr.contact_phone, emp.role, emp.experience
from public.user as usr
inner join public.employee as emp on usr.id = emp.id;


-- name: block_user_by_id!
update public.user
set is_active = FALSE
where id = :user_id;