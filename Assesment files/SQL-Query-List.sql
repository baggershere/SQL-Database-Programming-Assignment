-- A
INSERT INTO spectator (sno, sname, semail) VALUES (6, 'James May', 'james.may@gmail.com');

-- B
INSERT INTO event (ecode, edesc, elocation, edate, etime, emax) VALUES ('B100', '100m bicycle', 'Bath', '2019-04-19', '10:00', 600);

-- C
DELETE FROM spectator s
WHERE s.sno = {sno}
AND s.sno NOT IN (SELECT ticket.sno FROM ticket); 

-- D
DELETE FROM event e
WHERE e.ecode = 'S400'
AND e.ecode NOT IN (SELECT ticket.ecode FROM ticket);

-- E
INSERT INTO ticket (tno, ecode, sno) 
SELECT @tno, @ecode, @sno
WHERE -- check event exists
@ecode IN (SELECT ecode FROM event)
AND -- check customer doesn’t already have a ticket to that event
NOT EXISTS (
	SELECT ecode, sno FROM ticket
	WHERE ecode = @ecode AND sno = @sno
)
AND -- check that ticket limit emax has not been reached
((SELECT COUNT(ecode) FROM ticket WHERE ecode = @ecode) < 
(SELECT emax FROM event WHERE event.ecode = @ecode));

-- P
CREATE OR REPLACE VIEW viewp AS
SELECT edate, elocation, COUNT(ticket.ecode)
FROM event
LEFT JOIN ticket ON event.ecode = ticket.ecode
GROUP BY edate, elocation;

-- Q
CREATE OR REPLACE VIEW viewq AS
SELECT ticket.ecode, event.edesc, COUNT(tno) FROM ticket
LEFT JOIN event ON ticket.ecode = event.ecode
GROUP BY ticket.ecode, event.edesc
ORDER BY edesc;
SELECT * FROM viewq;

-- R
CREATE OR REPLACE VIEW viewr AS
SELECT ticket.ecode, event.edesc, COUNT(tno) FROM ticket
LEFT JOIN event ON ticket.ecode = event.ecode
WHERE ticket.ecode = 'A100'
GROUP BY ticket.ecode, event.edesc;
SELECT * FROM viewr;

-- S 
-- DROP TABLE sitinerary;
CREATE TABLE IF NOT EXISTS sitinerary (
	sno integer NOT NULL REFERENCES spectator(sno),
	sname VARCHAR(20) NOT NULL,
	ecode VARCHAR(20),
	edate DATE NOT NULL,
	elocation VARCHAR(20) NOT NULL,
	etime TIME NOT NULL,
	edesc VARCHAR(20) NOT NULL
);
INSERT INTO sitinerary (sno, sname, ecode, edate, elocation, etime, edesc)
SELECT ticket.sno, spectator.sname, event.ecode, event.edate, event.elocation, event.etime, event.edesc 
FROM ticket
INNER JOIN event ON ticket.ecode = event.ecode
INNER JOIN spectator ON ticket.sno = spectator.sno
WHERE ticket.sno = 4;

SELECT * FROM sitinerary;

--T
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

-- Create a view that contains every ticket by using SQL union. This view also uses the above function to state whether the ticket is valid or not. 
CREATE OR REPLACE VIEW all_tickets AS
SELECT tno, ecode, sno, check_ticket_in_ticket(tno) FROM ticket
UNION ALL
SELECT tno, ecode, sno, check_ticket_in_ticket(tno) FROM cancel;
-- Create a final view that joins the above view to the spectator table in order to get the spectator’s name.
CREATE OR REPLACE VIEW all_tickets_with_info AS
SELECT all_tickets.tno, all_tickets.ecode, all_tickets.sno, all_tickets.check_ticket_in_ticket, spectator.sname
FROM all_tickets
LEFT JOIN spectator ON all_tickets.sno = spectator.sno;

SELECT * FROM all_tickets_with_info;

--V
SELECT tno, ecode, sno, check_ticket_in_ticket as ticket_status, sname FROM all_tickets_with_info
WHERE ecode = ‘S400’ AND check_ticket_in_ticket =  false;
