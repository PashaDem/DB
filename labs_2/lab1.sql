-- first task
CREATE TABLE MyTable (id NUMBER, val number);

SELECT * FROM MyTable;

SELECT count(*) FROM MyTable;

DELETE FROM MyTable;


-- second task
DECLARE
	inserted_number NUMBER;
BEGIN
	FOR counter IN 0 .. 10000 LOOP
		SELECT ROUND(DBMS_RANDOM.VALUE (1, 1000)) INTO inserted_number FROM dual;
		INSERT INTO MyTable (id, val) VALUES (counter, inserted_number);
		dbms_output.put_line(inserted_number);
	END LOOP;
END;

-- third task
CREATE OR REPLACE FUNCTION does_more_even RETURN varchar2 AS 
	even_count number;
	odd_count number;
BEGIN 
	SELECT count(*) INTO even_count FROM MyTable WHERE MOD(val, 2) = 0;
	SELECT count(*) INTO odd_count FROM MyTable WHERE mod(val, 2) = 1;
	dbms_output.put_line(even_count);
	dbms_output.put_line(odd_count);

	IF even_count > odd_count THEN
		RETURN 'TRUE';
	ELSIF odd_count > even_count THEN 
		RETURN 'FALSE';
	END IF;

	RETURN 'EQUAL';
END;

SELECT does_more_even FROM dual;

-- forth task
CREATE OR REPLACE FUNCTION insert_generator (id_ int DEFAULT 0) RETURN varchar2 AS 
val_value NUMBER;
BEGIN 
	SELECT val INTO val_value FROM MyTable WHERE id = id_;
	RETURN 'insert into MyTable (id, val) values (' || TO_CHAR(id_) || ', ' || TO_CHAR(val_value) || ');';
END;

SELECT val FROM MyTable WHERE id = 2;

SELECT insert_generator(2) FROM dual;

--fifth task
CREATE OR REPLACE FUNCTION total_salary (month_salary NUMBER, year_premial_percent INT) RETURN NUMBER AS 
floating_percent NUMBER;
exc EXCEPTION;
bonus NUMBER;
BEGIN 
	
	IF month_salary < 0 OR year_premial_percent < 0 THEN
		raise exc;
	END IF;

	floating_percent := year_premial_percent / 100;
	bonus := (1 + floating_percent) * 12 * month_salary;
	
	RETURN bonus;
END;

SELECT total_salary(100, 2) FROM dual; 		-- 1224
SELECT total_salary(100, -1) FROM dual; 	-- exception
