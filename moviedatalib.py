""" Libray to store and access information extracted from IMDb

author:     Fabian Galetzka
Mail:       fabian.galetzka@volkswagen.de
latest:     31.01.2019
Version:    1.0


Contains the free classes:

DataMovie   Stores facts and trivia about a movie.
DataPerson  Stores facts and trivia about a person.
Trivia      Stores detailed information about trivia.
"""


# ---------------------------------------------------------------------------------------------------------------------
# --- DataMovie Class -------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
class DataMovie:
    def __init__(self,
                 title):    # A string. Should be the title of the movie.
        self.title = title
        self._facts = {}
        self._trivia_ref = None
        self._person_ref = {}

    def add_fact(self, key, fact):
        """ Adds a fact to the movie.

        Args:
            key     A string. The fact-type.
            fact    A string. The fact itself.
        """
        self._facts[key] = fact

    def has_fact(self, key):
        """ Checks if a fact is available

        Args:
            key     A string. The fact-type.

        Returns:
            Boolean Whether the fact is available or not.
        """
        return key in self._facts

    def get_fact(self, key):
        """ Returns a given fact.

        Args:
            key     A string. The fact-type.

        Returns:
            string  The fact.
        """
        return self._facts[key]

    def add_person_reference(self, key_person, person):
        self._person_ref[key_person] = person

    def has_person_fact(self, person, key):
        return self._person_ref[person].has_fact(key)

    def get_person_fact(self, person, key):
        return self._person_ref[person].get_fact(key)

    def add_trivia_reference(self, trivia):
        self._trivia_ref = trivia

    def has_unused_trivia(self, key_entity, entity):
        if key_entity == self.title and self._trivia_ref is not None:
            return self._trivia_ref.has_unused_trivia(entity)
        if key_entity in self._person_ref:
            return self._person_ref[key_entity].has_unused_trivia(entity)
        return 0

    def get_unused_trivia(self, key_entity, entity):
        if key_entity == self.title and self._trivia_ref is not None:
            return self._trivia_ref.get_unused_trivia(entity)
        if DataMovie._list_string_check(list=self._person_ref, object=key_entity):
            return self._person_ref[str(key_entity)].get_unused_trivia(entity)

    def get_trivia_entities(self, key_entity, trivia):
        if key_entity == self.title and self._trivia_ref is not None:
            return self._trivia_ref.get_entities(trivia)
        if DataMovie._list_string_check(list=self._person_ref, object=key_entity):
            return self._person_ref[str(key_entity)].get_trivia_entities(trivia)

    @staticmethod
    def _list_string_check(list, object):
        """ Checks if any objects name matches an objects name in a list. """
        for item in list:
            if str(object) == str(item):
                return True
        return False


# ---------------------------------------------------------------------------------------------------------------------
# --- DataPerson Class ------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
class DataPerson:
    def __init__(self, name):
        self.name = name
        self._facts = {}
        self._trivia_ref = None

    def add_fact(self, key, fact):
        self._facts[key] = fact

    def has_fact(self, key):
        return key in self._facts

    def get_fact(self, key):
        return self._facts[key]

    def add_trivia_reference(self, trivia):
        self._trivia_ref = trivia

    def has_unused_trivia(self, entity):
        if self._trivia_ref is not None:
            return self._trivia_ref.has_unused_trivia(entity)
        return 0

    def get_unused_trivia(self, entity):
        return self._trivia_ref.get_unused_trivia(entity)

    def get_trivia_entities(self, trivia):
        return self._trivia_ref.get_entities(trivia)


# ---------------------------------------------------------------------------------------------------------------------
# --- Trivia Class ----------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
class Trivia:
    def __init__(self, entity, trivia_dict):
        self.entity = entity
        self._trivia = trivia_dict
        self._trivia['used'] = []

    def has_unused_trivia(self, entity):
        if entity not in self._trivia:
            return 0
        num_of_trivia = len(self._trivia[entity])
        num_of_used_trivia = 0
        for trivia in self._trivia[entity]:
            if trivia in self._trivia['used']:
                num_of_used_trivia += 1.
        return num_of_trivia - num_of_used_trivia

    def get_unused_trivia(self, entity):
        for trivia in self._trivia[entity]:
            if trivia not in self._trivia['used']:
                self._trivia['used'].append(trivia)
                return trivia
        raise Exception("No unused trivia available. Check with has_unused_trivia() before calling get_unused_trivia!")

    def get_entities(self, trivia):
        trivia_list = []
        for entity in self._trivia:
            for trivia_ in self._trivia[entity]:
                if trivia == trivia_:
                    trivia_list.append(entity)
        return trivia_list
