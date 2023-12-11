-- name: does_company_exist_for_user_by_id^
select company_id
from public.client
where id = :user_id;

-- name: create_company!
CALL insert_and_map_company(:user_id, :name, :type, :show_in_partners);

-- name: get_company_by_id^
select *
from public.company
where id = :company_id;

-- name: get_company_by_user_id^
select *
from public.company as comp
         inner join public.client as cl on comp.id = cl.company_id
where cl.id = :user_id;

-- name: get_company_by_name^
select *
from public.company
where name = :name;


-- name: get_partner_companies
select *
from public.company
where show_in_partners = TRUE;

-- name: get_companies
select *
from public.company;

-- name: update_company_by_id!
update public.company
set name             = :name,
    type             = :type,
    show_in_partners = :show_in_partners
where id = :company_id;

-- name: delete_company_by_id!
delete
from public.company
where id = :company_id;

-- name: unbind_company_by_user_id!
CALL unbind_company(:user_id);