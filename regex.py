import re, string

# Constants

_loglim = 50

class SedError(Exception):
    """
    Raised when the format for substituion is incorrect
    """
    pass

def _validate(segments):
    """
    Determines whether the input violates any of the sed
    conventions.

    If everything is fine, nothing happens. If there
    is an error, the SedError exception is raised.
    """
    if len(segments) != 3:
        raise SedError("Missing \'/\' in the body of pattern.")
    elif re.match('[^ig]', segments[2]):
        raise SedError("Unknown flag for regular expression.")

def _parse_log(expression, loglist):
    """
    Find the most recent match of the user-
    input regular expression in the log.

    There is a hard cutoff for this (Default: 50).

    Returns a boolean True and the match if found
    otherwise returns False and None.
    """
    for i in range(1,_loglim+1):
        match = loglist[-i]['message']
        if expression.match(match):
            return True, loglist[-i]
    else:
        return False, None

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
        text = re.sub('s/', '', text)
        segments = text.split("/")
        try:
            _validate(segments)
        except SedError:
            content['message'] = "Your flag(s) and/or your use of slashes is incorrect."
            return content
        try:
            if 'i' in segments[2]:
                test = re.compile(segments[0], re.IGNORECASE)
            else:
                test = re.compile(segments[0])
            matchconfirm, matcheddict = _parse_log(test, self.log.data[content['channel']])
            if not matchconfirm:
                content['message'] = "A recent match was not found."
                return content
            if 'g' in segments[2]:
                out, _ = test.subn(segments[1], matcheddict['message'])
            else:
                out = test.sub(segments[1], matcheddict['message'])
            content['message'] = "<" + matcheddict['name'] + "> " + out
            return content
        except re.error:
            content['message'] = "The regular expression incurred an error."
            return content
