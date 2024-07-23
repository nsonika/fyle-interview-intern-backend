-- Write query to find the number of grade A's given by the teacher who has graded the most assignments

SELECT count(*) FROM assignments WHERE grade = 'A' AND teacher_id = (SELECT teacher_id FROM assignments WHERE grade IS NOT NULL GROUP BY teacher_id ORDER BY count(*) DESC LIMIT 1);