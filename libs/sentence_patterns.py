from numpy import random as rnd


class Questions:
    @staticmethod
    def budget(movie, seed=None):
        string = [
            "Ask for budget.",
            "Budget of '" + str(movie) + "'?",
            "Total cost of '" + str(movie) + "'?",
        ]
        Questions.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def year(movie, seed=None):
        string = [
            "Ask for release date.",
            "Ask for release year.",
            "Release year of '" + str(movie) + "'?",
            "Release date of '" + str(movie) + "'?",
        ]
        Questions.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def certificate(movie, seed=None):
        string = [
            "Ask for age restriction.",
            "Ask for age certification.",
            "Age restriction of '" + str(movie) + "'?",
            "Age certificate of '" + str(movie) + "'?",
        ]
        Questions.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def actor(movie, seed=None):
        string = [
            "Ask for actor in '" + str(movie) + "'.",
            "Actor in '" + str(movie) + "'?",
            "Who plays in '" + str(movie) + "'?",
            "Ask for the role of a mentioned actor in '" + str(movie) + "'.",
            "Role of a mentioned actor in '" + str(movie) + "'?",
            "Which role had a mentioned actor in '" + str(movie) + "'?"
        ]
        Questions.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def writer(movie, seed=None):
        string = [
            "Ask for writer of '" + str(movie) + "'.",
            "Writer of '" + str(movie) + "'?",
            "Who wrote '" + str(movie) + "'?",
        ]
        Questions.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def director(movie, seed=None):
        string = [
            "Ask for director of '" + str(movie) + "'.",
            "Director of '" + str(movie) + "'?",
            "Who directed '" + str(movie) + "'?",
        ]
        Questions.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def countries(movie, seed=None):
        string = [
            "Where was '" + str(movie) + "' shot?",
            "Shot location of '" + str(movie) + "'?"
        ]
        Questions.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def genres(movie, seed=None):
        string = [
            "Genre of '" + str(movie) + "'.",
            "What genre is '" + str(movie) + "'?",
            "Genres of '" + str(movie) + "'?",
        ]
        Questions.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def age(actor, seed=None):
        Questions.__set_seed(seed)
        string = [
            "Ask for age.",
            "Age of " + str(actor) + "?",
            "How old is " + str(actor) + "?",
        ]
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def movie_act(actor, seed=None):
        Questions.__set_seed(seed)
        string = [
            "A movie with '" + str(actor) + "'?",
            "In which movie did '" + str(actor) + "' play?"
        ]
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def __set_seed(seed):
        if seed:
            rnd.seed(seed)


class Facts:
    @staticmethod
    def actor(movie, actor, character=None, seed=None):
        if character:
            string = [
                "'" + str(actor) + "' plays '" + str(character) + "' in '" + str(movie) + "'.",
                "'" + str(actor) + "' plays in '" + str(movie) + "' (Role: '" + str(character) + "')."
            ]
            return string[int(rnd.rand() * len(string))]
        string = [
            "'" + str(movie) + "' stars '" + str(actor) + "'.",
            "'" + str(actor) + "' plays in '" + str(movie) + "'.",
        ]
        Facts.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def director(movie, director, seed=None):
        string = [
            "Director: " + str(director) + ".",
            "Director of '" + str(movie) + "' is '" + str(director) + "'.",
            "'" + str(director) + "' is the director of '" + str(movie) + "'.",
        ]
        Facts.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def writer(movie, writer, seed=None):
        string = [
            "Writer: " + str(writer) + ".",
            "Writer of '" + str(movie) + "' is '" + str(writer) + "'.",
            "'" + str(writer) + "' is the writer of '" + str(movie) + "'.",
        ]
        Facts.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def year(movie, year, seed=None):
        string = [
            "Year: " + str(year) + ".",
            "Release year of '" + str(movie) + "' was " + str(year) + ".",
            str(year) + " was the release year of '" + str(movie) + "'.",
        ]
        Facts.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def countries(movie, countries, seed=None):
        if len(countries) == 1:
            country = countries[0]
        else:
            country = countries[0] + " and " + countries[1]
        string = [
            "Location: " + str(country) + ".",
            "Was shot in " + str(country) + ".",
            str(movie) + " was shot in " + str(country) + "."
        ]
        Facts.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def budget(movie, budget, seed=None):
        string = [
            "Budget: " + str(budget) + ".",
            "Budget of " + str(movie) + " was " + str(budget) + ".",
            str(budget) + " was the budget of " + str(movie) + ".",
        ]
        Facts.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def certificate(movie, certificate, seed=None):
        string = [
            "Age certificate: " + str(certificate) + ".",
            "Age restriction of '" + str(movie) + "' is " + str(certificate) + ".",
            str(certificate) + " is the age restriction of '" + str(movie) + "'.",
        ]
        Facts.__set_seed(seed)
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def genres(genres):
        string = "Genres: "
        if len(genres) == 1:
            return "Genre: " + str(genres[0])
        # for genre in genres[0:len(genres)-1]:
        #     string += genre
        #     string += ", "
        else:
            return "Genre: " + str(genres[0]) + " and " + str(genres[1]) + "."
        # string += genres[-1]
        # string += "."
        # return string

    @staticmethod
    def age(actor, age, seed=None):
        Facts.__set_seed(seed)
        string = [
            str(actor) + " is " + str(age) + " years old.",
            "Age: " + str(age) + " years."
        ]
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def movie_act(actor, movie, char=None, seed=None):
        Facts.__set_seed(seed)
        if char:
            string = [
                "'" + str(actor) + "' played '" + str(char) + "' in '" + str(movie) + "'.",
                "'" + str(actor) + "' played in '" + str(movie) + "' (Role: '" + str(char) + "')."
            ]
        else:
            string = [
                "'" + str(actor) + "' played in '" + str(movie) + "'."
            ]
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def __set_seed(seed):
        if seed:
            rnd.seed(seed)


class Attitudes:
    @staticmethod
    def genre(genre, attitude=None, seed=None):
        if not attitude:
            Attitudes.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
        Attitudes.__set_seed(seed)
        if attitude == "positive":
            string = [
                "I like " + str(genre) + " movies.",
                str(genre) + " movies are my favorite.",
                "I love " + str(genre) + " movies.",
                str(genre) + " is a nice genre."
            ]
        elif attitude == "negative":
            string = [
                "I don't like " + str(genre) + " movies.",
                "I'm not interested in " + str(genre) + " movies.",
                # "I hate " + str(genre) + " movies.",
                str(genre) + " is a bad genre."
            ]
        elif attitude == "unknown":
            string = [
                "I don't know " + str(genre) + " movies.",
                "I don't know the genre " + str(genre) + "."
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def movie(movie, attitude=None, seed=None):
        if not attitude:
            Attitudes.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
        Attitudes.__set_seed(seed)
        if attitude == "positive":
            string = [
                "I like " + str(movie) + ".",
                str(movie) + " is my favorite movie.",
                "I love " + str(movie) + ".",
                str(movie) + " is a nice movie."
            ]
        elif attitude == "negative":
            string = [
                "I don't like " + str(movie) + " .",
                # "I hate " + str(movie) + ".",
                str(movie) + " is a bad movie."
            ]
        elif attitude == "unknown":
            string = [
                # "I'm not interested in " + str(movie) + " movies.",
                "I don't know " + str(movie) + ".",
                "I don't know the movie " + str(movie) + "."
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def person(person, type="actor", attitude=None, seed=None):
        if not attitude:
            Attitudes.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
        Attitudes.__set_seed(seed)
        if attitude == "positive":
            string = [
                "I like " + str(person) + ".",
                str(person) + " is my favorite " + type + ".",
                "I love " + str(person) + ".",
                str(person) + " is a nice " + type + "."
            ]
        elif attitude == "negative":
            string = [
                "I don't like " + str(person) + " .",
                # "I hate " + str(person) + ".",
                str(person) + " is a bad " + type + "."
            ]
        elif attitude == "unknown":
            string = [
                "I don't know " + str(person) + ".",
                "I don't know the " + str(type) + " " + str(person) + "."
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def certificate(movie, attitude=None, seed=None):
        if not attitude:
            Attitudes.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
        Attitudes.__set_seed(seed)
        if attitude == "positive":
            string = [
                "Age restriction: I agree.",
                "Age restriction of " + str(movie) + ": I agree.",
            ]
        elif attitude == "negative":
            string = [
                "Age restriction: To high.",
                "Age restriction: To low.",
            ]
        elif attitude == "unknown":
            string = [
                "No opinion about age restriction.",
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def countries(countries, attitude=None, seed=None):
        if not attitude:
            Attitudes.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
        country = countries[0]
        Attitudes.__set_seed(seed)
        if attitude == "positive":
            string = [
                "I like " + str(country) + "."
            ]
        elif attitude == "negative":
            string = [
                "I don't like " + str(country) + "."
            ]
        elif attitude == "unknown":
            string = [
                "I don't know much about " + str(country) + "."
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def __set_seed(seed):
        if seed:
            rnd.seed(seed)


class AttitudesV2:
    @staticmethod
    def genre(genre, attitude=None, seed=None, return_all=False, strength=0):
        if not attitude:
            AttitudesV2.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
            AttitudesV2.__set_seed(seed)
        if attitude == "positive":
            if return_all:
                strength = strength
            else:
                strength = rnd.random_integers(low=1, high=8)
            if strength == 1:
                string = [
                    str(genre) + " is my favorite genre.",
                    str(genre) + " is the best genre.",
                    str(genre) + " movies are my favorite.",
                    str(genre) + " movies are the best."
                ]
            elif 1 < strength <= 3:
                string = [
                    "I like the " + str(genre) + " very much.",
                    str(genre) + " is a very good genre.",
                    "I like " + str(genre) + " movies very much.",
                    str(genre) + " movies are very good."
                ]
            else:
                string = [
                    "I like the " + str(genre) + " genre.",
                    str(genre) + " is a good genre.",
                    "I like " + str(genre) + " movies.",
                    str(genre) + " movies are good."
                ]
        elif attitude == "negative":
            if return_all:
                strength = strength
            else:
                strength = rnd.random_integers(low=1, high=3)
            if strength == 1:
                string = [
                    str(genre) + " is a bad genre.",
                    str(genre) + " movies are bad."
                ]
            else:
                string = [
                    "I don't like the " + str(genre) + " genre.",
                    str(genre) + " is not a good genre.",
                    "I don't like " + str(genre) + " movies.",
                    str(genre) + " movies are not good."
                ]
        elif attitude == "unknown":
            string = [
                "I don't know " + str(genre) + " movies.",
                "I don't know the genre " + str(genre) + "."
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")

        attitude, _ = AttitudesV2.__choose_one_random(candidates=string)
        attitude_pattern = AttitudesV2.__generate_placeholder_pattern(attitude=attitude, entity1=genre,
                                                                      replace1="GENRE")
        if return_all:
            return string
        return attitude, attitude_pattern

    @staticmethod
    def movie(movie, attitude=None, seed=None, return_all=False, strength=0):
        if not attitude:
            AttitudesV2.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
            AttitudesV2.__set_seed(seed)
        string = ""
        if attitude == "positive":
            if return_all:
                strength = strength
            else:
                strength = rnd.random_integers(low=1, high=6)
            if strength == 1:
                string = [
                    "'" + str(movie) + "' is my favorite movie.",
                    "'" + str(movie) + "' is the best movie."
                ]
            elif 1 < strength <= 2:
                string = [
                    "I like '" + str(movie) + "' very much.",
                    "'" + str(movie) + "' is very good."
                ]
            else:
                string = [
                    "I like '" + str(movie) + "'.",
                    "'" + str(movie) + "' is good."
                ]
        elif attitude == "negative":
            if return_all:
                strength = strength
            else:
                strength = rnd.random_integers(low=1, high=3)
            if strength == 1:
                string = [
                    "'" + str(movie) + "' is a bad movie.",
                    "I really don't like '" + str(movie) + "'."
                ]
            else:
                string = [
                    "I don't like '" + str(movie) + "'.",
                    "'" + str(movie) + "' is not a good movie.",
                ]
        elif attitude == "unknown":
            string = [
                # "I don't know " + str(movie) + ".",
                "I don't know the movie '" + str(movie) + "'."
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")

        attitude, _ = AttitudesV2.__choose_one_random(candidates=string)
        attitude_pattern = AttitudesV2.__generate_placeholder_pattern(attitude=attitude, entity1=movie,
                                                                      replace1="MOVIE")
        if return_all:
            return string
        return attitude, attitude_pattern

    @staticmethod
    def person(person, type="actor", attitude=None, seed=None, return_all=False, strength=0):
        if not attitude:
            AttitudesV2.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
            AttitudesV2.__set_seed(seed)
        string = ""
        if attitude == "positive":
            if return_all:
                strength = strength
            else:
                strength = rnd.random_integers(low=1, high=6)
            if strength == 1:
                string = [
                    str(person) + " is my favorite " + str(type) + ".",
                    str(person) + " is the best " + str(type) + "."
                ]
            elif 1 < strength <= 2:
                string = [
                    "I like " + str(person) + " very much.",
                    str(person) + " is very good."
                ]
            else:
                string = [
                    "I like " + str(person) + ".",
                    str(person) + " is good."
                ]
        elif attitude == "negative":
            if return_all:
                strength = strength
            else:
                strength = rnd.random_integers(low=1, high=3)
            if strength == 1:
                string = [
                    str(person) + " is a bad " + str(type) + ".",
                    "I really don't like " + str(person) + " ."
                ]
            else:
                string = [
                    "I don't like " + str(person) + ".",
                    str(person) + " is not a good " + str(type) + ".",
                ]
        elif attitude == "unknown":
            string = [
                "I don't know " + str(person) + ".",
                "I don't know the " + str(type) + " " + str(person) + "."
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")

        attitude, _ = AttitudesV2.__choose_one_random(candidates=string)
        attitude_pattern = AttitudesV2.__generate_placeholder_pattern(attitude=attitude, entity1=person,
                                                                      replace1="PERSON", entity2=type,
                                                                      replace2="TYPE")
        if return_all:
            return string
        return attitude, attitude_pattern

    @staticmethod
    def certificate(movie, attitude=None, seed=None, return_all=False):
        if not attitude:
            AttitudesV2.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
            AttitudesV2.__set_seed(seed)
        if attitude == "positive":
            string = [
                "Age restriction: I agree.",
                "Age restriction of " + str(movie) + ": I agree.",
            ]
        elif attitude == "negative":
            string = [
                "Age restriction: Too high.",
                "Age restriction: Too low.",
                "I disagree with the age restriction.",
            ]
        elif attitude == "unknown":
            string = [
                "No opinion about age restriction.",
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")
        attitude, _ = AttitudesV2.__choose_one_random(candidates=string)
        attitude_pattern = AttitudesV2.__generate_placeholder_pattern(attitude=attitude, entity1=movie,
                                                                      replace1="MOVIE")
        if return_all:
            return string
        return attitude, attitude_pattern

    @staticmethod
    def countries(countries, attitude=None, seed=None, return_all=False, strength=0):
        if not attitude:
            AttitudesV2.__set_seed(seed)
            attitude = rnd.choice(["positive", "negative", "unknown"])
        country = countries[0]
        AttitudesV2.__set_seed(seed)
        string = ""
        if attitude == "positive":
            if return_all:
                strength = strength
            else:
                strength = rnd.random_integers(low=1, high=6)
            if strength == 1:
                string = [
                    str(country) + " is my favorite country.",
                ]
            elif 1 < strength <= 2:
                string = [
                    "I like " + str(country) + " very much.",
                ]
            else:
                string = [
                    "I like " + str(country) + ".",
                ]
        elif attitude == "negative":
            if return_all:
                strength = strength
            else:
                strength = rnd.random_integers(low=1, high=3)
            if strength == 1:
                string = [
                    "I really don't like " + str(country) + "."
                ]
            else:
                string = [
                    "I don't like " + str(country) + ".",
                ]
        elif attitude == "unknown":
            string = [
                "I don't know much about " + str(country) + ".",
                "I don't know " + str(country) + "."
            ]
        else:
            raise Exception("Key 'attitude' needs to be either 'positive', 'negative' "
                            "or 'unknown', not: '" + str(attitude) + "'.")
        attitude, _ = AttitudesV2.__choose_one_random(candidates=string)
        attitude_pattern = AttitudesV2.__generate_placeholder_pattern(attitude=attitude, entity1=country,
                                                                      replace1="COUNTRY")
        if return_all:
            return string
        return attitude, attitude_pattern

    @staticmethod
    def __set_seed(seed):
        if seed:
            rnd.seed(seed)

    @staticmethod
    def __choose_one_random(candidates):
        idx = int(rnd.rand() * len(candidates))
        return candidates[idx], idx

    @staticmethod
    def __generate_placeholder_pattern(attitude, entity1, replace1, entity2=None, replace2=None):
        attitude = attitude.replace(entity1, replace1)
        if entity2 is not None:
            attitude = attitude.replace(entity2, replace2)
        return attitude


class PersonFacts:
    @staticmethod
    def age(actor, age, seed=None):
        PersonFacts.__set_seed(seed)
        string = [
            str(actor) + " is " + str(age) + " years old.",
            "Age: " + str(age) + " years."
        ]
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def __set_seed(seed):
        if seed:
            rnd.seed(seed)


class PersonQuestions:
    @staticmethod
    def age(actor, seed=None):
        PersonQuestions.__set_seed(seed)
        string = [
            "Ask for age.",
            "Age of " + str(actor) + "?",
            "How old is " + str(actor) + "?",
        ]
        return string[int(rnd.rand() * len(string))]

    @staticmethod
    def __set_seed(seed):
        if seed:
            rnd.seed(seed)


if __name__ == "__main__":
    att = AttitudesV2()

    for idx in range(10):
        a, b = att.countries(countries=["Deutschland"])
        print("Attitude: " + a)
        print("Pattern:  " + b)

        a, b = att.movie(movie="Pulp Fiction")
        print("Attitude: " + a)
        print("Pattern:  " + b)

        a, b = att.person("Fabian Galetzka", "Doktorand")
        print("Attitude: " + a)
        print("Pattern:  " + b)

        a, b = att.genre("Action")
        print("Attitude: " + a)
        print("Pattern:  " + b)

        a, b = att.certificate("Pulp Fiction")
        print("Attitude: " + a)
        print("Pattern:  " + b)


    # for idx in range(10):
    #     print(att.movie("MOVIE", 'positive'))
    # for idx in range(5):
    #     print(att.movie("MOVIE", 'negative'))
    # for idx in range(5):
    #     print(att.movie("MOVIE", 'unknown'))
    #
    # for idx in range(10):
    #     print(att.person("ACTOR", "person", 'positive'))
    # for idx in range(5):
    #     print(att.person("ACTOR", "person",  'negative'))
    # for idx in range(5):
    #     print(att.person("ACTOR", "person",  'unknown'))

    # for idx in range(10):
    #     print(att.genre("ACTOR", 'positive'))
    # for idx in range(5):
    #     print(att.genre("ACTOR",  'negative'))
    # for idx in range(5):
    #     print(att.genre("ACTOR",  'unknown'))

    # for idx in range(10):
    #     print(att.countries("GERMANY", 'positive'))
    # for idx in range(5):
    #     print(att.countries("GERMANY",  'negative'))
    # for idx in range(5):
    #     print(att.countries("GERMANY",  'unknown'))

    # for idx in range(10):
    #     print(att.certificate("ELEVEN", 'positive'))
    # for idx in range(5):
    #     print(att.certificate("ELEVEN",  'negative'))
    # for idx in range(5):
    #     print(att.certificate("ELEVEN",  'unknown'))
