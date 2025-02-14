# REGEX
regex_decimal_from_0_to_infinity = "^[0-9]+(\\.[0-9]+)?$"
regex_integer_from_1_to_infinity = "^[1-9][0-9]*$"
# Adjust `2` after `|` operator if higher top limit is desired. Example: `[2-9][0-9]{3}$` -> from 2000 to 9999
regex_integer_from_1900_to_2999 = "^(19[0-9]{2}|2[0-9]{3})$"
