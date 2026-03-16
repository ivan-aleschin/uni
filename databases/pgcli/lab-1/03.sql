SET search_path = bookings;

SELECT 
    t.passenger_name, 
    s.price
FROM tickets t
JOIN segments s ON t.ticket_no = s.ticket_no
WHERE s.price = (SELECT MAX(price) FROM segments)
ORDER BY t.passenger_name;
