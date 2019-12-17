SELECT
    column_name(s)
FROM
    table_name
WHERE
    column_name operator ALL
    (
        SELECT
            column_name
        FROM
            table_name
        WHERE
            condition);
INSERT INTO
    Product_D
VALUES
    ('B',  1158,  'PC'),
    ('C',  2190,  'Laptop'),
    ('D',  3219,  'Printer');
SELECT
    field_1,
    field_2,
    CAST(DATE_FORMAT(CASE WHEN LENGTH(sale_date) > 10 THEN SUBSTRING(sale_date, 1,  10) ELSE sale_date END,  'u') as int),
    SUM(field_3)  AS field_3,
    MAX(field_2)
FROM
    my_table
LEFT JOIN
    (
        SELECT
            field_2,
            SUM(field_1)
        FROM
            (
                SELECT
                    field_2,
                    field_1
                FROM
                    another_table) AS b
        GROUP BY
            field_2) AS sub_table_on
ON
    my_table.field_2  =  sub_table.field_2
LEFT JOIN
    table_three
ON
    my_table.field_1  =  table_three.field_1
GROUP BY
    field_1,  field_2
ORDER BY
    field_1 DESC