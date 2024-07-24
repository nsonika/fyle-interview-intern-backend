-- Write query to find the number of grade A's given by the teacher who has graded the most assignments

-- SELECT count(*) FROM assignments WHERE grade = 'A' AND teacher_id = (SELECT teacher_id FROM assignments WHERE grade IS NOT NULL GROUP BY teacher_id ORDER BY count(*) DESC LIMIT 1);

WITH teacher_grades AS (
    SELECT teacher_id, 
           COUNT(*) AS total_graded, 
           SUM(CASE WHEN grade = 'A' THEN 1 ELSE 0 END) AS grade_a_count
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
)
SELECT grade_a_count
FROM teacher_grades
ORDER BY total_graded DESC
LIMIT 1;
