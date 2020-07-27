def tuple_space_set_length(tup, string_len = 80):

    '''
    Takes a tuple of two strings and puts a certain amount of spaces between
    them depending on the string_len


    '''

    len_tup_1 = len(tup[0])
    len_tup_2 = len(tup[1])

    spaces_needed = string_len - sum([len_tup_1, len_tup_2])

    return tup[0] + ' ' * spaces_needed + tup[1]


def centered_text(phrase, line_length = 80):

    side_spaces = int((line_length - len(phrase)) / 2)
    return "{}{}{}".format(" " * side_spaces, phrase, " " * side_spaces)
