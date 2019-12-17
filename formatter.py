import re
import keywords
import config


def clean_sql(sql):
    """Clean the sql, remove all \n to flat the sql. """
    flat_sql = sql.replace('\n', ' ').strip()
    return flat_sql


def add_endl_after_word(word, text):
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(word.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l + len(word)] + '\n' + text[index_l + len(word):]
        idx = index_l + len(word) + 1
    return text


def find_keywords(sql, keywords_list):
    """Find all the keywords in `sql`.

    :param sql: The sql string being manipulated.
    :param keywords_list: A list of all the keywords being found in sql.
    :return: A dictionary with keys of sql keywords and values of two element lists with the starting and ending indexes of the keywords.
    """
    keyword_positions = []
    sql_len = len(sql)
    jude_list = [' ', '\n', '(', ')', '\t', ',']
    for n in range(sql_len):
        for kw in keywords_list:
            if sql[n:n + len(kw)].lower() == kw.lower():
                pre_single = False
                suf_single = False
                if (n == 0) or (sql[n - 1] in jude_list):
                    pre_single = True
                if (n == (sql_len - len(kw))) or (sql[n + len(kw)] in jude_list):
                    suf_single = True
                single = all([pre_single, suf_single])
                if single:
                    keyword_positions.append([sql[n:n + len(kw)], n, n + len(kw)])

    to_delete = []
    for kw1 in keyword_positions:
        for kw2 in keyword_positions:
            if (kw1[0].lower() in kw2[0].lower()) & (len(kw1[0]) < len(kw2[0])) & (kw1[1] >= kw2[1]) & (
                    kw2[2] <= kw2[2]):
                to_delete.append(kw1)

    for n in to_delete:
        if n in keyword_positions:
            keyword_positions.remove(n)

    keyword_positions = sorted(keyword_positions, key=lambda x: x[1])
    return keyword_positions


def line_keywords(sql, keyword_loc, wrap_keywords):
    """Add the \n to each key words.

    :param sql: The sql string being manipulated.
    :param keyword_loc: The location of key words.
    :param wrap_keywords: Wrap keywords.
    :return: String
    """
    offset = 0
    for i in keyword_loc:
        print(i)
        if i[0].lower() in wrap_keywords:
            sql = sql[:(i[1] + offset)] + '\n' + i[0] + '\n' + sql[(i[2] + offset):]
            offset += 2

    sql = sql.replace('\n\n', '\n')
    if sql[0] == '\n':
        sql = sql.replace(sql, sql[1:len(sql)])
    return sql


def coma_handler(sql):
    if config.new_line_after_comma:
        sql = sql.replace(',', ',' + '\n')
    if config.space_before_coma:
        sql = sql.replace(',', ' ,')
    if config.space_after_coma:
        sql = sql.replace(',', ', ')
    return sql


def space_arround_operators(sql):
    if config.space_arround_operators:
        for i in keywords.operators:
            #pattern = re.compile('[^ ]' + i)
            #sql = re.sub(r"\S" % i, ' ' + i, sql)
            sql = sql.replace(i, ' ' + i + ' ')
    return sql


def split_wrap(sql):
    """Split with \n, and strip the ' '. """
    sql_list = sql.split('\n')
    if sql_list[0] == '':
        del sql_list[0]
    if sql_list[-1] == '':
        del sql_list[-1]
    sql_list = list(map(lambda x: x.strip(), sql_list))
    return sql_list


def str_mode_change(sql_list, wrap_keywords, func_keywords):
    """Change the key words. Upper, lower or change nothing. """
    if config.word_case == "":
        return sql_list
    else:
        for i, frag in enumerate(sql_list):
            if frag.lower() in wrap_keywords:
                sql_list[i] = frag.lower() if config.word_case == "LOWER" else frag.upper()
                continue
            func_list = []
            for func_v in func_keywords:
                if func_v in frag.lower():
                    func_list.append(func_v)
            if len(func_list) > 0:
                mark_frag = frag.lower() if config.word_case == "LOWER" else frag.upper()
                func_loc = find_keywords(frag, func_list)
                for loc in func_loc:
                    frag = frag[:loc[1]] + mark_frag[loc[1]:loc[2]] + frag[loc[2]:]
                sql_list[i] = frag
        return sql_list


def add_indent(sql_list, wrap_keywords):
    """Add the indent. """
    indent_space = ''
    for i in range(config.indent_size):
        indent_space += ' '
    default_num = 1
    inner_num = 0
    count_left = 0
    count_right = 0
    for i, frag in enumerate(sql_list):
        if frag.lower() not in wrap_keywords:
            sql_list[i] = (default_num + inner_num * 2) * indent_space + frag
        if (frag.lower() in wrap_keywords) and (inner_num > 0):
            sql_list[i] = inner_num * 2 * indent_space + frag
        count_left += len(re.findall('\(', frag))
        count_right += len(re.findall('\)', frag))
        inner_num = count_left - count_right
    return sql_list


def into_handler(sql):
    if config.move_into_to_a_new_line:
        sql = add_endl_after_word('insert', sql)
    if config.move_clause_after_into_to_a_new_line:
        sql = add_endl_after_word('into', sql)
    if config.new_line_after_comma_insert:
        start = sql.lower().find('values')
        while start != -1:
            end = sql.find(';', start+1)
            sql_substr = sql[start:end].replace('),', '),\n')
            sql = sql[:start] + sql_substr + sql[end:]
            start = sql.lower().find('values', start+1)
    return sql


def select_handler(sql):
    if config.new_line_after_all_distinct:
        sql = add_endl_after_word('all', sql)
        sql = add_endl_after_word('distinct', sql)
    if config.wrap_elements_select:
        start = sql.lower().find('select')
        while start != -1:
            end = sql.lower().find('from', start + 1)
            bracket_count = 0
            cur_ind = start
            for i in sql[start:end]:
                if i == '(':
                    bracket_count += 1
                if i == ')':
                    bracket_count -= 1
                if i == ',' and bracket_count == 0:
                    print(cur_ind)
                    cur_ind += 1
                    sql = sql[:cur_ind] + '\n' + sql[cur_ind:]
                cur_ind += 1
            start = sql.lower().find('select', start+1)
    return sql


def formatter(sql):  # , wrap_add=None):
    """Format the sql string.

    :param sql: The input sql
    :param wrap_add: Add some string to wrap a line, such as ',', 'and'
    :param mode: 'none', 'upper', 'lower'. key words lower(upper), no change.
    :return: Formatted sql string.
    """

    flat_sql = clean_sql(sql)
    wrap_keywords_loc = find_keywords(flat_sql, keywords.wrap_keywords)

    sql = line_keywords(flat_sql, wrap_keywords_loc, keywords.wrap_keywords)
    sql = coma_handler(sql)
    sql = space_arround_operators(sql)
    sql = into_handler(sql)
    sql = select_handler(sql)
    sql_list = split_wrap(sql)
    sql_list = str_mode_change(sql_list, keywords.wrap_keywords, keywords.func_keywords)
    sql_list = add_indent(sql_list, keywords.wrap_keywords)

    format_sql = '\n'.join(sql_list)

    return format_sql


def read_file(input_file):
    with open(input_file) as f:
        raw_sql = f.read()
    return raw_sql


def write_file(sql, output_file):
    with open(output_file, 'w') as f:
        f.write(sql)

