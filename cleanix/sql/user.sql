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
select usr.id, usr.username, usr.fullname, usr.contact_phone, emp.role, emp.experience
from public.user as usr
inner join public.employee as emp on usr.id = emp.id;

--name: get_user_info_by_user_id^
select u.id as id,
       e.role as role,
       u.fullname as fullname,
       u.contact_phone as contact_phone,
       u.username as username,
       u.is_active as is_active,
       u.is_employee as is_employee,
       s.left_feedback as left_feedback
from public.user u
left join public.employee e on u.id = e.id
left join public.client c on c.id = u.id
left join public.statistics s on s.id = c.statistics_id
where u.id = :user_id;

-- name: block_user_by_id!
update public.user
set is_active = FALSE
where id = :user_id;


-- name: get_employees
select * from public.user u
inner join public.employee e on u.id = e.id where u.id != :current_user_id;