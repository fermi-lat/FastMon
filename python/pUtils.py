## @package pUtils
## @brief Package containing utilities of general interest.

import logging

## @brief Expand a specified string to a given length added spaces on the
#  right.
#
#  If the string is longer than the specified length, it is truncated on the
#  right, instead. Useful for printing on the screen formatted text.
## @param string
#  The string to be formatted.
## @param length
#  The goal string length.

def expandString(string, length=10):
    try:
        if len(string) > length:
            return string[:length]
        numSpaces = length - len(string)
        return '%s%s' % (string, ' '*numSpaces)
    except:
        return string


## @brief Format a number with a given number of decimal places, then expand
#  it as a string of given length.
## @param number
#  The real number to be formatted.
## @param numDecPlaces
#  The number of decimal places required.
## @param length
#  The goal string length.

def expandNumber(number, numDecPlaces=3, length=10):
    try:
        formatSpec = '%s.%df' % ('%', numDecPlaces)
        string = formatSpec % number
        return expandString(string, length)
    except:
        return expandString(number, length)


if __name__ == '__main__':
    print '"%s"' % expandString('test')
    print '"%s"' % expandString('test', 8)
    print '"%s"' % expandNumber(1.236547)
