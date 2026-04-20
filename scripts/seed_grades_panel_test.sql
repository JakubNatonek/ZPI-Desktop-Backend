BEGIN;

-- 1) Role required by grades panel
INSERT INTO roles (name)
SELECT v.name
FROM (VALUES ('admin'), ('student'), ('wykladowca')) AS v(name)
WHERE NOT EXISTS (
    SELECT 1
    FROM roles r
    WHERE r.name = v.name
);

-- 2) Department for test users
INSERT INTO departments (name, abbreviation)
SELECT 'Informatyka Test', 'WIT'
WHERE NOT EXISTS (
    SELECT 1
    FROM departments d
    WHERE d.name = 'Informatyka Test' OR d.abbreviation = 'WIT'
);

-- 3) Subjects visible/editable for lecturer role "wykladowca" (type = wyklad)
INSERT INTO subject (name, type, type_display, room_properties, blocked, periodic)
SELECT 'Programowanie obiektowe', 'wyklad', 'W', 'wykladowa', FALSE, TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM subject s
    WHERE s.name = 'Programowanie obiektowe' AND s.type = 'wyklad'
);

INSERT INTO subject (name, type, type_display, room_properties, blocked, periodic)
SELECT 'Bazy danych', 'wyklad', 'W', 'wykladowa', FALSE, TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM subject s
    WHERE s.name = 'Bazy danych' AND s.type = 'wyklad'
);

-- 4) Ensure there is an active semester (required by lecturer edit restrictions)
INSERT INTO semesters (data_rozpoczecia, data_zakonczenia, nazwa)
SELECT (CURRENT_DATE - INTERVAL '30 days')::date,
       (CURRENT_DATE + INTERVAL '180 days')::date,
       'Semestr testowy panelu ocen'
WHERE NOT EXISTS (
    SELECT 1
    FROM semesters s
    WHERE s.data_rozpoczecia <= CURRENT_DATE
      AND s.data_zakonczenia >= CURRENT_DATE
);

-- 4b) Ensure there is one previous semester for UI switching tests
INSERT INTO semesters (data_rozpoczecia, data_zakonczenia, nazwa)
SELECT (CURRENT_DATE - INTERVAL '240 days')::date,
     (CURRENT_DATE - INTERVAL '60 days')::date,
     'Semestr testowy panelu ocen - poprzedni'
WHERE NOT EXISTS (
  SELECT 1
  FROM semesters s
  WHERE s.nazwa = 'Semestr testowy panelu ocen - poprzedni'
);

-- 5) Test users (password for all: test123)
-- bcrypt hash generated with app.auth.password_utils.hash_password('test123')
INSERT INTO users (
    first_name,
    last_name,
    album_number,
    login,
    email,
    public_key,
    password_hash,
    must_change_password,
    is_blocked,
    last_seen_at
)
VALUES
  ('Test', 'Student', '99011', 'student.oceny.test', 'student.oceny.test@uczelnia.pl', NULL, '$2b$12$.j0mjk9oHKO83aOhPHrE8uMPqMQZ69WHTRZFAgve92AXPQAoibyii', FALSE, FALSE, NULL),
  ('Test', 'Wykladowca', '99012', 'wykladowca.oceny.test', 'wykladowca.oceny.test@uczelnia.pl', NULL, '$2b$12$.j0mjk9oHKO83aOhPHrE8uMPqMQZ69WHTRZFAgve92AXPQAoibyii', FALSE, FALSE, NULL),
  ('Test', 'Admin', '99013', 'admin.oceny.test', 'admin.oceny.test@uczelnia.pl', NULL, '$2b$12$.j0mjk9oHKO83aOhPHrE8uMPqMQZ69WHTRZFAgve92AXPQAoibyii', FALSE, FALSE, NULL)
ON CONFLICT (login) DO NOTHING;

-- Keep credentials and emails stable on reruns
UPDATE users
SET
  email = CASE login
    WHEN 'student.oceny.test' THEN 'student.oceny.test@uczelnia.pl'
    WHEN 'wykladowca.oceny.test' THEN 'wykladowca.oceny.test@uczelnia.pl'
    WHEN 'admin.oceny.test' THEN 'admin.oceny.test@uczelnia.pl'
    ELSE email
  END,
    password_hash = '$2b$12$.j0mjk9oHKO83aOhPHrE8uMPqMQZ69WHTRZFAgve92AXPQAoibyii',
    must_change_password = FALSE,
    is_blocked = FALSE
WHERE login IN ('student.oceny.test', 'wykladowca.oceny.test', 'admin.oceny.test');

-- 6) Role assignments
INSERT INTO roles_for_user (user_id, role_id)
SELECT u.user_id, r.id
FROM users u
JOIN roles r ON r.name = 'student'
WHERE u.login = 'student.oceny.test'
  AND NOT EXISTS (
      SELECT 1
      FROM roles_for_user x
      WHERE x.user_id = u.user_id AND x.role_id = r.id
  );

INSERT INTO roles_for_user (user_id, role_id)
SELECT u.user_id, r.id
FROM users u
JOIN roles r ON r.name = 'wykladowca'
WHERE u.login = 'wykladowca.oceny.test'
  AND NOT EXISTS (
      SELECT 1
      FROM roles_for_user x
      WHERE x.user_id = u.user_id AND x.role_id = r.id
  );

INSERT INTO roles_for_user (user_id, role_id)
SELECT u.user_id, r.id
FROM users u
JOIN roles r ON r.name = 'admin'
WHERE u.login = 'admin.oceny.test'
  AND NOT EXISTS (
      SELECT 1
      FROM roles_for_user x
      WHERE x.user_id = u.user_id AND x.role_id = r.id
  );

-- 7) Department assignments
INSERT INTO departments_for_user (user_id, department_id)
SELECT u.user_id, d.id
FROM users u
JOIN departments d ON d.abbreviation = 'WIT'
WHERE u.login IN ('student.oceny.test', 'wykladowca.oceny.test', 'admin.oceny.test')
  AND NOT EXISTS (
      SELECT 1
      FROM departments_for_user x
      WHERE x.user_id = u.user_id AND x.department_id = d.id
  );

-- 8) Student/teacher profiles
INSERT INTO student (user_id, index_number, group_id, semester)
SELECT u.user_id, '990001', NULL, 1
FROM users u
WHERE u.login = 'student.oceny.test'
  AND NOT EXISTS (
      SELECT 1
      FROM student s
      WHERE s.user_id = u.user_id
  );

INSERT INTO teacher (user_id, title, prop)
SELECT u.user_id, 'dr', 'adiunkt'
FROM users u
WHERE u.login = 'wykladowca.oceny.test'
  AND NOT EXISTS (
      SELECT 1
      FROM teacher t
      WHERE t.user_id = u.user_id
  );

-- 9) Replace test grades for current active semester
WITH ctx AS (
    SELECT
        (SELECT user_id FROM users WHERE login = 'student.oceny.test') AS student_id,
        (SELECT user_id FROM users WHERE login = 'wykladowca.oceny.test') AS lecturer_id,
        (
            SELECT id
            FROM semesters
            WHERE data_rozpoczecia <= CURRENT_DATE
              AND data_zakonczenia >= CURRENT_DATE
            ORDER BY id DESC
            LIMIT 1
        ) AS semester_id
)
DELETE FROM grade_records g
USING ctx
WHERE g.student_id = ctx.student_id
  AND g.lecturer_id = ctx.lecturer_id
  AND g.semester = ctx.semester_id
  AND g.subject_name IN ('Programowanie obiektowe', 'Bazy danych');

WITH ctx AS (
    SELECT
        (SELECT user_id FROM users WHERE login = 'student.oceny.test') AS student_id,
        (SELECT user_id FROM users WHERE login = 'wykladowca.oceny.test') AS lecturer_id,
        (
            SELECT id
            FROM semesters
            WHERE data_rozpoczecia <= CURRENT_DATE
              AND data_zakonczenia >= CURRENT_DATE
            ORDER BY id DESC
            LIMIT 1
        ) AS semester_id
)
INSERT INTO grade_records (
    student_id,
    lecturer_id,
    semester,
    subject_name,
    component_label,
    component_info,
    grade_value,
    weight,
    is_final,
    sort_order
)
SELECT
    ctx.student_id,
    ctx.lecturer_id,
    ctx.semester_id,
    v.subject_name,
    v.component_label,
    v.component_info,
    v.grade_value,
    v.weight,
    v.is_final,
    v.sort_order
FROM ctx
JOIN (
    VALUES
        ('Programowanie obiektowe', 'Ocena koncowa', '', 4.5::float, 5.0::float, TRUE, 0),
        ('Programowanie obiektowe', 'Kolokwium 1', 'teoria', 4.0::float, 0.4::float, FALSE, 1),
        ('Programowanie obiektowe', 'Projekt', 'implementacja', 5.0::float, 0.6::float, FALSE, 2),
        ('Bazy danych', 'Ocena koncowa', '', 4.0::float, 4.0::float, TRUE, 0),
        ('Bazy danych', 'Kolokwium', 'SQL', 3.5::float, 0.5::float, FALSE, 1),
        ('Bazy danych', 'Laboratorium', 'cwiczenia praktyczne', 4.0::float, 0.5::float, FALSE, 2)
) AS v(subject_name, component_label, component_info, grade_value, weight, is_final, sort_order) ON TRUE
WHERE ctx.student_id IS NOT NULL
  AND ctx.lecturer_id IS NOT NULL
  AND ctx.semester_id IS NOT NULL;

-- 10) Replace test grades for an additional previous semester
WITH ctx AS (
  SELECT
    (SELECT user_id FROM users WHERE login = 'student.oceny.test') AS student_id,
    (SELECT user_id FROM users WHERE login = 'wykladowca.oceny.test') AS lecturer_id,
    (
      SELECT id
      FROM semesters
      WHERE nazwa = 'Semestr testowy panelu ocen - poprzedni'
      ORDER BY id DESC
      LIMIT 1
    ) AS semester_id
)
DELETE FROM grade_records g
USING ctx
WHERE g.student_id = ctx.student_id
  AND g.lecturer_id = ctx.lecturer_id
  AND g.semester = ctx.semester_id
  AND g.subject_name IN ('Programowanie obiektowe', 'Bazy danych');

WITH ctx AS (
  SELECT
    (SELECT user_id FROM users WHERE login = 'student.oceny.test') AS student_id,
    (SELECT user_id FROM users WHERE login = 'wykladowca.oceny.test') AS lecturer_id,
    (
      SELECT id
      FROM semesters
      WHERE nazwa = 'Semestr testowy panelu ocen - poprzedni'
      ORDER BY id DESC
      LIMIT 1
    ) AS semester_id
)
INSERT INTO grade_records (
  student_id,
  lecturer_id,
  semester,
  subject_name,
  component_label,
  component_info,
  grade_value,
  weight,
  is_final,
  sort_order
)
SELECT
  ctx.student_id,
  ctx.lecturer_id,
  ctx.semester_id,
  v.subject_name,
  v.component_label,
  v.component_info,
  v.grade_value,
  v.weight,
  v.is_final,
  v.sort_order
FROM ctx
JOIN (
  VALUES
    ('Programowanie obiektowe', 'Ocena koncowa', '', 4.0::float, 5.0::float, TRUE, 0),
    ('Programowanie obiektowe', 'Kolokwium 1', 'teoria', 3.5::float, 0.4::float, FALSE, 1),
    ('Programowanie obiektowe', 'Projekt', 'implementacja', 4.5::float, 0.6::float, FALSE, 2),
    ('Bazy danych', 'Ocena koncowa', '', 3.5::float, 4.0::float, TRUE, 0),
    ('Bazy danych', 'Kolokwium', 'SQL', 3.0::float, 0.5::float, FALSE, 1),
    ('Bazy danych', 'Laboratorium', 'cwiczenia praktyczne', 4.0::float, 0.5::float, FALSE, 2)
) AS v(subject_name, component_label, component_info, grade_value, weight, is_final, sort_order) ON TRUE
WHERE ctx.student_id IS NOT NULL
  AND ctx.lecturer_id IS NOT NULL
  AND ctx.semester_id IS NOT NULL;

COMMIT;

-- Optional quick checks:
-- 1) SELECT login, album_number FROM users WHERE login IN ('student.oceny.test', 'wykladowca.oceny.test', 'admin.oceny.test');
-- 2) SELECT semester, subject_name, component_label, grade_value, weight, is_final FROM grade_records
--    WHERE student_id = (SELECT user_id FROM users WHERE login = 'student.oceny.test')
--    ORDER BY subject_name, sort_order;
