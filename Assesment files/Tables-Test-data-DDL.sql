CREATE TABLE event (
ecode CHAR(4) NOT NULL PRIMARY KEY,
edesc VARCHAR(20) NOT NULL,
elocation VARCHAR(20) NOT NULL,
edate DATE NOT NULL,
CHECK (edate >= '2019-04-01' AND edate <= '2019-04-30'),
etime TIME NOT NULL,
CHECK (etime >= '09:00:00'),
emax SMALLINT NOT NULL,
CHECK (emax >= 1 AND emax <= 1000)
);

CREATE TABLE spectator (
sno INTEGER NOT NULL PRIMARY KEY,
sname VARCHAR(20) NOT NULL,
semail VARCHAR(100) NOT NULL 
);

CREATE TABLE ticket (
tno INTEGER NOT NULL PRIMARY KEY,
ecode CHAR(4) NOT NULL REFERENCES event (ecode)  ON DELETE CASCADE,
sno INTEGER NOT NULL REFERENCES spectator (sno)
);

CREATE TABLE cancel (
tno INTEGER NOT NULL PRIMARY KEY,
ecode CHAR(4) NOT NULL,
sno INTEGER REFERENCES spectator (sno) ON DELETE SET NULL,
cdate TIMESTAMP NOT NULL DEFAULT NOW(),
cuser VARCHAR(128) NOT NULL DEFAULT 1
);


-- TEST DATA 
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('S400', '400m swimming event', 'London', '2019-04-28', '10:00:00', 450);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('S600', '400m swim', 'Stadium 1', '2019-04-01', '09:00:00', 100);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('S900', '400m swim', 'Stadium 1', '2019-04-01', '09:00:00', 100);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('S200', '400m swim', 'Stadium 1', '2019-04-01', '09:00:00', 100);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('I54D', 'lorem id', 'Lodan Wetan', '2019-04-10', '17:55:00', 91);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('U55A', 'imperdiet sapien', 'Perehonivka', '2019-04-12', '14:26:00', 66);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('P55L', 'dolor vel est donec', 'Trzcinica', '2019-04-06', '11:03:00', 62);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('K55Z', 'eu felis', 'Embi', '2019-04-12', '12:01:00', 56);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('I55D', 'consequat metus', 'Bantarsari Kulon', '2019-04-06', '11:03:00', 48);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('N44L', 'et magnis', 'Beverwijk', '2019-04-23', '12:13:00', 95);
INSERT INTO public.event (ecode, edesc, elocation, edate, etime, emax) VALUES ('P54T', 'nonummy', 'Lapa do Lobo', '2019-04-26', '13:20:00', 28);

INSERT INTO public.spectator (sno, sname, semail) VALUES (2, 'Sam Bagnall', 'sam.bagnall@gmail.com');
INSERT INTO public.spectator (sno, sname, semail) VALUES (3, 'Anna Bagnall', 'anna.bagnall@gmail.com');
INSERT INTO public.spectator (sno, sname, semail) VALUES (4, 'Sarah Hodgson', 'sarah.hodgson@gmail.com');
INSERT INTO public.spectator (sno, sname, semail) VALUES (5, 'Dave', 'd@d.com');
INSERT INTO public.spectator (sno, sname, semail) VALUES (6, 'David', 'dav@fa.com');
INSERT INTO public.spectator (sno, sname, semail) VALUES (7, 'Dave', 'd@d.com');
INSERT INTO public.spectator (sno, sname, semail) VALUES (8, 'David', 'dav@fa.com');


INSERT INTO public.ticket (tno, ecode, sno) VALUES (2, 'S200', 2);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (3, 'S400', 4);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (4, 'P55L', 4);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (5, 'S600', 3);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (6, 'S600', 3);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (7, 'P55L', 5);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (8, 'S200', 8);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (9, 'S400', 7);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (10, 'P55L', 7);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (11, 'S600', 8);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (12, 'S600', 6);
INSERT INTO public.ticket (tno, ecode, sno) VALUES (13, 'P55L', 6);

INSERT INTO public.cancel (tno, ecode, sno, cdate, cuser) VALUES (50, 'P54T', 8, '2019-04-06', 1);
INSERT INTO public.cancel (tno, ecode, sno, cdate, cuser) VALUES (51, 'P54T', 6, '2019-04-07', 1);
INSERT INTO public.cancel (tno, ecode, sno, cdate, cuser) VALUES (52, 'S400', 4, '2019-04-08', 1);
INSERT INTO public.cancel (tno, ecode, sno, cdate, cuser) VALUES (53, 'P55L', 3, '2019-04-09', 1);
INSERT INTO public.cancel (tno, ecode, sno, cdate, cuser) VALUES (54, 'P55L', 8, '2019-04-09', 1);



 Functions -- to be applied depending on test data as requirments unclear. **

 CREATE OR REPLACE FUNCTION delete_ticket_from_ticket() RETURNS trigger AS
 $BODY$
 BEGIN
 INSERT INTO cancel (tno, ecode, sno, cdate, cuser)
 VALUES (OLD.tno, old.ecode, old.sno, now(), 1);
 RETURN OLD;
 END;
 $BODY$
 LANGUAGE plpgsql;

 CREATE TRIGGER delete_from_ticket
 BEFORE DELETE
 ON ticket
 FOR EACH ROW
 EXECUTE PROCEDURE delete_ticket_from_ticket();

-- *************************************************************************************************

CREATE OR REPLACE FUNCTION add_ticket_to_cancel() RETURNS trigger AS
$$
BEGIN

IF EXISTS (
SELECT ticket.tno
FROM ticket
WHERE ticket.tno = NEW.tno
) THEN
DELETE FROM ticket WHERE NEW.tno = ticket.tno;
RETURN NEW;
END IF;
RETURN NEW;

END
$$ LANGUAGE plpgsql;

CREATE TRIGGER add_ticket_to_cancel
AFTER INSERT
ON cancel
FOR EACH ROW
EXECUTE PROCEDURE add_ticket_to_cancel();


CREATE OR REPLACE FUNCTION check_ticket_in_ticket(tno int)
RETURNS BOOL AS
$$
BEGIN
	IF EXISTS (SELECT ticket.tno FROM ticket WHERE ticket.tno = $1) THEN
	RETURN TRUE;
	ELSE RETURN FALSE;
	END IF;
	RETURN TRUE;
END;		
$$
LANGUAGE plpgsql;





