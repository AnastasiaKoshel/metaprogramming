from formatter import formatter, config

conf = config.Config("../config")
inp = "C:/Users/Анастасия/Desktop/MetaProgJava/java_formatter/src/formatter/input.txt"
out = "C:/Users/Анастасия/Desktop/MetaProgJava/java_formatter/src/formatter/output.txt"
frm = formatter.Formatter(conf, inp, out)
frm.format_file()
