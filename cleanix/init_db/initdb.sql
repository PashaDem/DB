-- user logic

CREATE TABLE IF NOT EXISTS public.company
(
    id               serial                NOT NULL,
    name             character varying(50) NOT NULL UNIQUE,
    type             character varying(50) NOT NULL DEFAULT 'Not specified',
    show_in_partners bool                  NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.statistics
(
    id            serial           NOT NULL,
    orders_count  bigint           NOT NULL DEFAULT 0,
    total_price   double precision NOT NULL DEFAULT 0,
    left_feedback bool             NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.user
(
    id            serial       NOT NULL,
    username      varchar(50)  NOT NULL UNIQUE,
    password      varchar(100) NOT NULL,
    fullname      varchar(120) NOT NULL,
    contact_phone varchar(20)  NOT NULL,
    is_employee   bool         NOT NULL DEFAULT FALSE,
    is_active     bool         NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.employee
(
    id         serial           NOT NULL REFERENCES public.user (id) ON DELETE CASCADE,
    role       varchar(20)      NOT NULL,
    experience double precision NOT NULL,
    PRIMARY KEY (id),
    constraint check_role_name check ( role = 'EMPLOYEE' OR role = 'MANAGER' )
);

CREATE TABLE IF NOT EXISTS public.client
(
    id            serial NOT NULL REFERENCES public.user (id) ON DELETE CASCADE,
    company_id    bigint REFERENCES public.company (id) UNIQUE,
    statistics_id bigint NOT NULL REFERENCES public.statistics (id) UNIQUE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.feedback
(
    id          serial                 NOT NULL,
    create_at   date                   NOT NULL,
    score       integer                NOT NULL,
    description character varying(300) NOT NULL,
    client_id   bigint                 NOT NULL REFERENCES public.client (id) ON DELETE SET NULL,
    PRIMARY KEY (id),
    constraint check_score_value check ( score >= 1 and score <= 5 )
);

-- order logic

CREATE TABLE IF NOT EXISTS public.service
(
    id          serial                NOT NULL,
    type        character varying(50) NOT NULL DEFAULT 'Not specified',
    name        varchar(50)           NOT NULL UNIQUE,
    description character varying(100),
    price       double precision      NOT NULL DEFAULT 0,
    is_archived bool                  NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.tool
(
    id              serial                NOT NULL,
    name            character varying(50) NOT NULL UNIQUE,
    description     character varying(100),
    is_deregistered bool                  NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.transport
(
    id              serial       NOT NULL,
    name            varchar(50)  NOT NULL UNIQUE,
    brand           varchar(150) NOT NULL,
    description     text,
    is_deregistered bool         NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.contract
(
    id    serial           NOT NULL,
    price double precision NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.cleaning_order
(
    id          serial                 NOT NULL,
    address     character varying(100) NOT NULL,
    clean_date  date                   NOT NULL,
    client_id   bigint                 NOT NULL REFERENCES public.client (id),
    contract_id bigint                 NOT NULL REFERENCES public.contract (id),
    status      varchar(20)            NOT NULL DEFAULT 'INQUEUE',
    PRIMARY KEY (id),
    constraint check_status check ( status = 'INQUEUE' or status = 'INPROCESS' or status = 'PAID')
);

CREATE TABLE IF NOT EXISTS public.order_to_service
(
    service_id bigint NOT NULL REFERENCES public.service (id),
    order_id   bigint NOT NULL REFERENCES public.cleaning_order (id),
    PRIMARY KEY (service_id, order_id)
);

CREATE TABLE IF NOT EXISTS public.order_to_tool
(
    order_id bigint NOT NULL REFERENCES public.cleaning_order (id),
    tool_id  bigint NOT NULL REFERENCES public.tool (id),
    PRIMARY KEY (order_id, tool_id)
);

CREATE TABLE IF NOT EXISTS public.order_to_employee
(
    order_id    bigint NOT NULL REFERENCES public.cleaning_order (id),
    employee_id bigint NOT NULL REFERENCES public.employee (id),
    PRIMARY KEY (order_id, employee_id)
);

CREATE TABLE IF NOT EXISTS public.order_to_transport
(
    order_id     bigint REFERENCES public.cleaning_order (id),
    transport_id bigint REFERENCES public.transport (id),
    PRIMARY KEY (order_id, transport_id)
);

CREATE OR REPLACE PROCEDURE insert_full_client(username varchar, password varchar, fullname varchar,
                                               contact_phone varchar)
    LANGUAGE plpgsql
AS
$$
declare
    stat_id bigint;
    user_id bigint;
begin
    INSERT INTO "statistics" DEFAULT VALUES RETURNING id INTO stat_id;
    INSERT INTO public.user (USERNAME, PASSWORD, FULLNAME, CONTACT_PHONE, IS_EMPLOYEE)
    VALUES (username, password, fullname, contact_phone, FALSE)
    RETURNING id INTO user_id;
    INSERT INTO public.client (id, statistics_id) VALUES (user_id, stat_id);
end;
$$;

CREATE OR REPLACE PROCEDURE insert_full_employee(username varchar, password varchar, fullname varchar,
                                                 contact_phone varchar, role varchar, experience decimal)
    LANGUAGE plpgsql
AS
$$
declare
    user_id bigint;
begin
    INSERT INTO public.user (USERNAME, PASSWORD, FULLNAME, CONTACT_PHONE, IS_EMPLOYEE)
    VALUES (username, password, fullname, contact_phone, TRUE)
    RETURNING id INTO user_id;
    INSERT INTO public.employee (ID, ROLE, EXPERIENCE) VALUES (user_id, role, experience);
end;
$$;

CREATE OR REPLACE PROCEDURE insert_and_map_company(user_id integer, name_ varchar, type_ varchar, show_in_partners_ bool)
    LANGUAGE plpgsql
AS
$$
declare
    company_id_ bigint;
begin
    INSERT INTO public.company (name, type, show_in_partners)
    VALUES (name_, type_, show_in_partners_)
    RETURNING id INTO company_id_;
    UPDATE public.client SET company_id = company_id_ where id = user_id;
end;
$$;

CREATE OR REPLACE PROCEDURE unbind_company(user_id integer)
    LANGUAGE plpgsql
AS
$$
declare
    company_id_ integer;
begin
    SELECT company_id INTO company_id_ FROM client where id = user_id;
    UPDATE public.client SET company_id = NULL where id = user_id;
    DELETE FROM public.company WHERE id = company_id_;
end;
$$;

CREATE OR REPLACE FUNCTION insert_full_order(address_ varchar, clean_date_ date, client_id_ bigint,
                                             status_ varchar)
    RETURNS bigint
    LANGUAGE plpgsql
AS
$$
declare
    contract_id_ bigint;
    order_id_    bigint;
begin
    INSERT INTO public.contract (price) VALUES (0) RETURNING id INTO contract_id_;
    INSERT INTO public.cleaning_order (address, clean_date, client_id, contract_id, status)
    VALUES (address_, clean_date_, client_id_, contract_id_, status_)
    RETURNING id INTO order_id_;
    RETURN order_id_;
end;
$$;

CREATE OR REPLACE PROCEDURE append_new_service(service_ids int[], order_id_ int)
    LANGUAGE plpgsql
AS
$$
declare
begin
    for i in array_lower(service_ids, 1) .. array_upper(service_ids, 1)
        loop
            if service_ids[i] in (select service_id from public.order_to_service where order_id = order_id_) then
                raise notice 'service with id=% is already in the table.', service_ids[i];
            else
                insert into public.order_to_service (service_id, order_id) VALUES (service_ids[i], order_id_);
            end if;
        end loop;
end;
$$;


CREATE OR REPLACE PROCEDURE update_order_price(order_id_ bigint)
    LANGUAGE plpgsql
as
$$
DECLARE
    rec        record;
    result_sum double precision;
BEGIN
    select sum(price) as total_price
    into result_sum
    from order_to_service
             inner join service on service.id = order_to_service.service_id
    where order_id = order_id_;
    IF result_sum IS NULL THEN
        result_sum := 0;
    END IF;
    update contract
    set price = result_sum
    where id = (select contract_id from cleaning_order where cleaning_order.id = order_id_);
    raise notice 'new price %', result_sum;
END;
$$;

create or replace function update_contract_by_service_cost_change()
    returns trigger
    language plpgsql
as
$$
declare
    service_id_ bigint;
    rec         record;
begin
    IF NEW.price = OLD.price THEN
        raise notice 'Цена не поменялась, так что ничего пересчитывать не нужно';
        return NEW;
    END IF;
    service_id_ := NEW.id;
    for rec in select order_id, co.status
               from order_to_service as os
                        inner join cleaning_order as co on co.id = os.order_id
               where service_id = service_id_
        LOOP
            if rec.status = 'INQUEUE' then
                CALL update_order_price(rec.order_id);
            end if;

        END LOOP;
    return NEW;

end;
$$;

create or replace trigger update_order_cost_on_service_price_update
    after update
    on service
    for row
execute procedure update_contract_by_service_cost_change();


CREATE OR REPLACE FUNCTION update_contract_by_services_cost_change_by_insert()
    RETURNS TRIGGER
    LANGUAGE plpgsql
AS
$$
DECLARE
    identifier bigint;
    status_    varchar;
BEGIN
    identifier := NEW.order_id;
    select status into status_ from cleaning_order where id = identifier;
    if status_ = 'INQUEUE' then
        CALL update_order_price(identifier);
    end if;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER update_ord_cost_on_order_to_service_insert
    AFTER INSERT OR UPDATE
    ON order_to_service
    FOR ROW
EXECUTE PROCEDURE update_contract_by_services_cost_change_by_insert();

CREATE OR REPLACE FUNCTION update_contract_by_service_cost_change_by_delete()
    RETURNS TRIGGER
    LANGUAGE plpgsql
AS
$$
DECLARE
    identifier bigint;
    status_    varchar;
BEGIN
    identifier := OLD.order_id;
    SELECT status into status_ FROM cleaning_order where id = identifier;
    IF status_ = 'INQUEUE' THEN
        CALL update_order_price(identifier);
    END IF;
    RETURN OLD;
END;
$$;


CREATE OR REPLACE TRIGGER update_ord_cost_on_order_to_service_delete
    AFTER DELETE
    ON order_to_service
    FOR ROW
EXECUTE PROCEDURE update_contract_by_service_cost_change_by_delete();


CREATE OR REPLACE PROCEDURE increment_order_count(statistics_id_ bigint)
    LANGUAGE plpgsql
as
$$
declare
    current_order_count bigint;
begin
    SELECT orders_count INTO current_order_count from public.statistics where id = statistics_id_;
    update public.statistics set orders_count = current_order_count + 1 where id = statistics_id_;
end;
$$;


create or replace procedure decrement_orders_count(client_id_ integer)
    language plpgsql
as
$$
declare
    stats_id            bigint;
    current_order_count bigint;
begin
    select statistics_id
    into stats_id
    from public.client
    where id = client_id_;

    select orders_count
    into current_order_count
    from statistics
    where id = stats_id;

    update public.statistics
    set orders_count = current_order_count - 1
    where id = stats_id;
end;
$$;


CREATE OR REPLACE PROCEDURE update_total_cost_by_order_id(order_id_ bigint)
    language plpgsql
as
$$
declare
    client_id_         bigint;
    stat_id            bigint;
    current_total_cost decimal;
    order_price        decimal;
    contract_id_       bigint;
begin
    select client_id into client_id_ from cleaning_order where id = order_id_;
    select statistics_id into stat_id from client where id = client_id_;
    select total_price into current_total_cost from statistics where id = stat_id;
    select contract_id into contract_id_ from cleaning_order where id = order_id_;
    select price into order_price from contract where id = contract_id_;
    update statistics set total_price = current_total_cost + order_price where id = stat_id;
end;
$$;