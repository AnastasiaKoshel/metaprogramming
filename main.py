import config
import formatter

input_file = "input.sql"
output_file = "output.sql"

raw_sql = formatter.read_file(input_file)
format_sql = formatter.formatter(raw_sql)
formatter.write_file(format_sql, output_file)
