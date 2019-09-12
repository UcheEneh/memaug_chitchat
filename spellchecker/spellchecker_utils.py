""" Additional utility functions """
import sys
import re
import contextlib
import json

#print(sys.version_info)

@contextlib.contextmanager
def load_file(filename):
    try:
        with open(filename, "rt") as f:
            yield f.read()

    except Exception as e:
        print(e)
    
def _parse_into_words(text):
    """ Parse the text into words; currently removes punctuation
        
        Args:
            text (str): The text to split into words
    """
    # TODO: 
    # Check if using spaCy here is better
    res = re.findall(r"\w+", text.lower())
    return res

def load_entities(filename):
    """ Handle opening entity files correctly and
        reading all the data
        
        Args:
            filename (str): The filename to open
            #encoding (str): The file encoding to use
        Yields:
            str: The string data from the file read
    """
    #Check ner ExtractMovieEntities() later
    return False