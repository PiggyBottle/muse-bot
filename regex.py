import re, string

# Constants

_loglim = 50
_matchlim = 10
_regquant = False

class SedError(Exception):
    """
    Raised when the format for substituion is incorrect
    """
    pass

class QuantityError(Exception):
    """
    Raised when the quantity of matches in an expression
    exceeds the limit _matchlim.
    """
    pass

def _validate_slashes(segments):
    """
    Determines whether the input uses the correct formatting
    for replacement cases.

    If everything is fine, nothing happens. If there
    is an error, the SedError exception is raised.
    """
    if len(segments) != 3:
        raise SedError("Missing \'/\' in the body of pattern.")

def _validate_flags(segments):
    """
    Determines whether the input uses valid
    flags for regular expressions.

    If everything is fine, nothing happens. If there
    is an error, the SedError exception is raised.
    """
    if re.findall('[^ig]', segments[2]):
        raise SedError("Unknown flag for regular expression.")

def _parse_log(expression, loglist):
    """
    Find the most recent match of the user-
    input regular expression in the log.

    There is a hard cutoff for this (Default: 50).

    Returns a boolean True and the match if found
    otherwise returns False and None.
    """
    i = 1
    count = 0
    while count < _loglim+1:
        if loglist[-i]['type'] == 'PRIVMSG':
            match = loglist[-i]['message']
            if expression.findall(match):
                return True, loglist[-i]
            i += 1
            count += 1
        else:
            i += 1
            continue
    else:
        return False, None

def _positions(text, char):
    """
    A function to determine the indices in a string where
    characters are located.

    Returns a list of indices.
    """
    return [pos for pos, c in enumerate(text) if c == char]

def _validate_quant(segments):
    """
    Determines whether the number of matches in a {n, ...}
    term of a regular expression is within limitations.

    Raises QuantityError if the number of matches exceeds
    the limit.
    """

    expression = segments[0]
    if '{' in expression and '}' in expression:
        openind = _positions(expression, '{')
        closeind = _positions(expression, '}')
        for start in openind:
            for finish in closeind:
                if start < finish:
                    try:
                        for quants in expression[start+1:finish].split(","):
                            quants = int(quants)
                            if quants > _matchlim:
                                raise QuantityError
                    except ValueError:
                        pass

def _blockquant(segments):
    """
    Determines whether a quantifier is used in an expression.

    Returns a boolean True if there is a quantifier.
    """

    expression = segments[0]
    if '{' in expression and '}' in expression:
        openind = _positions(expression, '{')
        closeind = _positions(expression, '}')
        for start in openind:
            for finish in closeind:
                if start < finish:
                    try:
                        for quants in expression[start+1:finish].split(","):
                            quants = int(quants)
                            return True
                    except ValueError:
                        pass
        else:
            return False
    else:
        return False

def _sedsplit(text):
    """
    A function rigged to only split sed strings at non-escaped slashes.

    Returns a list of strings, separating `text` at the sed-style
    / separators.
    """
    split = []
    newstring = ""
    indices = _positions(text, "/")
    lastind = 0
    for i in range(0, len(indices)):
        if text[indices[i]-1] == "\\" and text[indices[i]-2] != "\\":
            newstring += text[lastind:indices[i]-1] + "/"
        else:
            newstring += text[lastind:indices[i]]
            split.append(newstring)
            newstring = ""
        lastind = indices[i] + 1
    if text[lastind:]:
        split.append(text[lastind:])
    else:
        split.append("")
    return split

class Regex():
    """
    A class that evaluates regular expression substitutions
    for IRC messages.

    The syntax for replacements is that of GNU `sed`:

    s/<Regex for text to be changed>/<Replacement text>/
    """

    def __init__(self, logger):
        self.log = logger

    def replace(self, content):
        """
        The actual substitution function.

        Given the user message, validate the format
        then determine the appropriate line to substitute
        using parse_log.

        The multiline flag is not included in this function
        because for this purpose it seems illogical.
        """
        text = content['message']
        text, _ = re.subn('s/', '', text, count=1)
        segments = _sedsplit(text)
        chanlog = self.log.data[content['channel']]
        try:
            _validate_slashes(segments)
        except SedError:
            content['message'] = "Your use of slashes is incorrect."
            return content
        try:
            _validate_flags(segments)
        except SedError:
            content['message'] = "\'" + segments[2] + "\' contains invalid flags."
            return content
        if _regquant:
            try:
                _validate_quant(segments)
            except QuantityError:
                content['message'] = "Attempted to match too large a quantity."
                return content
        else:
            blocked = _blockquant(segments)
            if blocked:
                content['message'] = "Quantifying has been blocked in regular expressions."
                return content
        try:
            if 'i' in segments[2]:
                test = re.compile(segments[0], re.IGNORECASE)
            else:
                test = re.compile(segments[0])
            matchconfirm, matcheddict = _parse_log(test, chanlog)
            if not matchconfirm:
                content['message'] = "A recent match was not found."
                return content
            if 'g' in segments[2]:
                out, _ = test.subn(segments[1], matcheddict['message'])
            else:
                out, _ = test.subn(segments[1], matcheddict['message'], count=1)
            content['message'] = "<" + matcheddict['name'] + "> " + out
            return content
        except re.error:
            content['message'] = "The regular expression incurred an error."
            return content
