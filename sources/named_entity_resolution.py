# import json
import pickle
import os
import copy
import time

import spacy
import re
import warnings
import string

from nltk import edit_distance, jaccard_distance
from nltk.tokenize import word_tokenize
from nltk.tokenize import WhitespaceTokenizer

from sources import contractions

# from imdb import IMDb
# from tqdm import tqdm
# from sources import reader as rdr


class ExtractMovieEntity:
    def __init__(self, path_data, already_loaded=False):
        self.path_full_data = path_data
        # For run_through_dialogue
        if already_loaded:
            self.full_data = path_data
            # print('Full movie database loaded!')
        else:
            # Load the database of collected movie information
            if not os.path.isfile(self.path_full_data):
                print("Database (data.pkl) of collected movie information not available in path given: ", path_data)
            else:
                with open(self.path_full_data, 'rb') as f:
                    self.full_data = pickle.load(f)
                    print('Full movie database loaded!')

    def create_dict_of_entities(self, _users=None, _log_text=None, logfile_info=None):
        """
        Create dicts of enitites:
            person entities, info entities and character entities
        """
        ###################################################
        #        GET THE NAME OF MAIN MOVIE IN LOG        #
        ###################################################
        if logfile_info is None:
            # I assume the first table fact entity from the first speaker is always the movie name
            # except for story of type: PersonToTrivia, where the movie name is the second entity
            # Maybe better way to get movie name
            person_story = False
            for item in _log_text:
                if item['type'] == 'story_type' and item['story_type'] == 'PersonToMovieStory':
                    person_story = True
                    break
            for item in _log_text:
                if item['type'] == 'table_facts' and item['user']['id'] == _users[0]:
                    if person_story is True:
                        movie_name = item['table'][0][2]
                    else:
                        movie_name = item['table'][0][0]
                    meetup_name = item['room']['name']
                    print("\nLog: ", meetup_name)
                    print("Movie name: ", movie_name)
                    print("-----------------------")
                    break
        # Read from processed log dialogue
        else:
            movie_name = logfile_info[0]
            meetup_name = logfile_info[1]
            print("\nLog: ", meetup_name)
            print("Movie name: ", movie_name)
            print("-----------------------")

        #########################################################
        #        CHECK IF MOVIE DATA IN CREATED DATABASE        #
        #########################################################
        self.title = None
        for movie in self.full_data['movies']:
            if movie_name == movie.title:
                self.title = movie.title
                break

        ########################################################################################
        #    CREATE A DICT WHICH CONTAINS ALL ENTITIES IN FACTS TABLE AND THEIR SUBSTITUTES    #
        ########################################################################################
        """
        # Entities we need to look for:
            actors, budget, certificate, countries, 
            director, genres, writer, year, character
        """
        list_actor, list_countries, list_genres, list_movies = ([], [], [], [])
        person_entities = {}  # actor, director, writer
        info_entities = {}  # movie title, budget, year, certificate,...
        character_entities = {}  # arranged according to actors

        #######################################
        #         Input main movie name        #
        #######################################
        if self.title not in list_movies:
            list_movies.append(self.title)
            info_entities.update({self.title: 'movie#' + str(len(list_movies) - 1)})
        # TO DO:
        # Check for other movies that may have been mentioned which isn't main movie

        ######################################
        #        Input other entities        #
        ######################################
        # for entity in tqdm(movie._facts):
        for entity in movie._facts:
            if entity == 'actors':
                actors = movie.get_fact('actors')
                for actor in actors:
                    # for actor and their role in movie._facts['actors']:
                    if str(actor) not in list_actor:
                        list_actor.append(str(actor))
                        person_entities.update({str(actor): 'actor#' + str(len(list_actor) - 1)})

                        # Character
                        character = actor.notes

                        regex_as = '\s?\(.* ?\)'
                        matches = re.finditer(regex_as, character, re.MULTILINE)
                        found = []
                        for match in matches:
                            found.append([match.start(), match.end()])
                        for index in found[::-1]:
                            character = character[:index[0]]

                        # Don't include characters with single letter as name
                        if len(character) != 1 and character != '':
                            character_entities.update({character: 'character#' + str(len(character_entities))})
                continue

            if entity == 'budget':
                # only one budget considered
                info_entities.update({movie.get_fact(entity): 'budget#0'})
                continue

            if entity == 'certificate':
                info_entities.update({movie.get_fact(entity): 'certificate#0'})
                continue

            if entity == 'countries':
                for country in movie._facts[entity]:
                    list_countries.append(country)
                    info_entities.update({country: 'country#' + str(len(list_countries) - 1)})
                continue

            if entity == 'genres':
                for genre in movie._facts[entity]:
                    list_genres.append(genre)
                    info_entities.update({genre: 'genre#' + str(len(list_genres) - 1)})
                continue

            if entity == 'year':
                # Release year
                # movie_entities.update({movie._facts[entity] : 'year#0'})
                info_entities.update({movie.get_fact(entity): 'year#0'})
                continue

        ###########################################
        #        Input director and writer        #
        ###########################################
        if movie.has_fact('writer=director'):  # or movie.has_fact('director'):
            if movie.get_fact('writer=director') is True:
                entity = str(movie.get_fact('director'))
                # only one director considered
                person_entities.update({entity: 'director#0'})
            else:
                entity = str(movie.get_fact('director'))
                person_entities.update({entity: 'director#0'})

                entity = str(movie.get_fact('writer'))
                person_entities.update({entity: 'writer#0'})
        else:
            entity = str(movie.get_fact('director'))
            person_entities.update({entity: 'director#0'})

            entity = str(movie.get_fact('writer'))
            person_entities.update({entity: 'writer#0'})

        return [person_entities, info_entities, character_entities], movie_name


class NamedEntityResolution:
    def __init__(self, path_data, path_logs=None, mturk_session=None):
        # self.path_results = os.path.join(path_logs + "/output/", mturk_session)
        self.path_logs = path_logs
        self.mturk_session = mturk_session
        self.names_list = None
        self.path_data = path_data
        self.nlp = spacy.load('en_core_web_lg')#('en_core_web_sm')

    def run_through_dialogue(self, dialogue, logfile_info, facts_original, attitudes_original):
        """
        :param dialogue: pointer
        :param facts_original:   pointer
        :param attitudes_original: pointer
        :return:
        """
        start = time.time()

        movie_data = self.path_data
        original_dialogue_ = copy.deepcopy(dialogue)

        mov_ent = ExtractMovieEntity(movie_data, already_loaded=True)
        entities_dict_full, mov_name = mov_ent.create_dict_of_entities(logfile_info=logfile_info)

        """ FOR DEBUG """
        self.entites_dict_full = entities_dict_full

        # Rearranged entities dict
        person_ent_dict, info_ent_dict, character_ent_dict = entities_dict_full
        rearranged_ent_list = [info_ent_dict, person_ent_dict, character_ent_dict]
        self.already_ner_dict = {}

        # ****************************************************
        # Perform facts and attitudes named entity resolution
        # ****************************************************
        facts_ner = copy.deepcopy(facts_original)
        attitudes_ner = copy.deepcopy(attitudes_original)
        facts_relations = {'has_writer': "writer",
                           'has_director': "director",
                           'has_actor': "actor",
                           'has_release_year': "year",
                           'has_shot_location': "country",
                           'has_budget': "budget",
                           'has_age_certificate': "certificate",
                           'has_genre': "genre",
                           'has_role': "character"}
        facts_relations_v2 = ['has_trivia', 'has_plot']

        facts_and_attitdues = [attitudes_ner, facts_ner]
        for a_or_f in facts_and_attitdues:
        # Loop through each speaker and their facts and attitudes triples
            for speaker, full_triple in a_or_f.items():
                # Assuming single speaker has multiple facts given, therefore multiple triples:
                for triple in full_triple:
                    # Facts table entity
                    for count, ent_dict in enumerate(rearranged_ent_list):
                        ##################################
                        # SUBJECT
                        ##################################
                        _subject = triple['subject']
                        if _subject in ent_dict:
                            if ent_dict[_subject][0:4] != 'char':    # skip for characters
                                if _subject in self.already_ner_dict:
                                    value = self.already_ner_dict[_subject]
                                else:
                                    value = self.update_new_value(_subject, ent_dict[_subject])
                                triple['subject'] = triple['subject'].replace(_subject, value)

                        ##################################
                        # OBJECT
                        ##################################
                        # Facts table value
                        _object = triple['object']
                        if triple['relation'] in facts_relations:
                            object_value = facts_relations[triple['relation']]
                            # convert to int for year entities
                            if count == 0 and triple['relation'] == 'has_release_year':
                                _object_ent = int(_object)
                            else:
                                _object_ent = _object
                            if _object_ent in ent_dict:
                                if ent_dict[_object_ent][0:4] == object_value[0:4]:
                                    if _object in self.already_ner_dict:
                                        value = self.already_ner_dict[_object]
                                    else:
                                        value = self.update_new_value(_object, ent_dict[_object_ent])
                                    triple['object'] = triple['object'].replace(_object, value)
                        # continue
                        elif triple['relation'] in facts_relations_v2:
                            for ent, val in ent_dict.items():
                                ent = str(ent)
                                if ent + ' ' in _object or ' ' + ent in _object:    # particularly helpful for genre (War)
                                    # ent_str = str(ent)
                                    # Don't use new entities for has_trivia and has_plot besides the one already seen.
                                    # So characters would not be included here as well except if has_role in relations
                                    if ent in self.already_ner_dict:
                                        value = self.already_ner_dict[ent]
                                        triple['object'] = triple['object'].replace(ent, value)
                                    # else:
                                        # value = self.update_new_value(_object, ent_dict[ent])
                                        # triple['object'] = triple['object'].replace(ent, value)

        # CREATE SECOND DICT TO RUN THE PROCESS ON:
        info_ent_dict_v2 = {}
        person_ent_dict_v2 = {}
        character_ent_dict_v2 = {}
        for key, value in self.already_ner_dict.items():
            if value[0:4] == 'acto' or value[0:4] == 'dire' or value[0:4] == 'writ':
                person_ent_dict_v2.update({key : value})
            elif value[0:4] == 'char':
                character_ent_dict_v2.update({key : value})
            else:
                info_ent_dict_v2.update({key : value})
        entities_dict_smaller = [person_ent_dict_v2, info_ent_dict_v2, character_ent_dict_v2]

        grouped_entities_dict = [entities_dict_smaller, entities_dict_full]
        self.original_dialogue_ner_small = []
        self.original_dialogue_ner_full = []

        # Check for different variations in movie name during entity resolution
        # For now only perform search if ':' is in movie name. Consider others later e.g ',!'
        self.names_list = []
        if ':' in mov_name:
            self.names_list = self._create_different_searches(mov_name, type="movie", characters=entities_dict_full[2])
        else:
            self.names_list.append(mov_name)

        self.list_US, self.list_UK = None, None
        # Check country and make list for entity resolution search if matching
        if "United States" in entities_dict_full[1]:
            self.list_US = self._create_different_searches(name="United States", type="country")
        if "United Kingdom" in entities_dict_full[1]:
            self.list_UK = self._create_different_searches(name="United Kingdom", type="country")

        print("\nEntities in the movie: ")
        print("Person: ")
        print(entities_dict_full[0])
        print("Info: ")
        print(entities_dict_full[1])
        print("Characters: ")
        print(entities_dict_full[2])
        print("-----------------------")

        self.found_person_not_in_entities_dict = {}
        for utterance in original_dialogue_:
            for count, single_entities_dict in enumerate(grouped_entities_dict):
                # Perform ner
                if count == 0:
                    utterance = self._implement_resolution(single_entities_dict, utterance, type='small')
                    print(utterance)
                    self.original_dialogue_ner_small.append(utterance.lower())
                elif count == 1:
                    utterance = self._implement_resolution(single_entities_dict, utterance, type='full')
                    if "i ' m" in utterance:
                        utterance = re.sub("i ' m", "i 'm", utterance)
                    self.printGreen(utterance)
                    self.original_dialogue_ner_full.append(utterance.lower())

        if self.found_person_not_in_entities_dict:
            self.printPurple('People not matching from the list of given entities: ')
            self.printPurple(self.found_person_not_in_entities_dict)

        # Check time spent for one dialogue
        end = time.time()
        print("\nProcessing time of dialogue: {0:.4f} secs".format(end-start))
        print("---------------------------: {0:.3f} mins".format((end-start)/ 60))

        # NOTE: The final_ent_dict would always be the full one since entities_dict_full is always second in the
        # for loop above
        # final_ent_dict = {**self.actor_ent, **self.non_actor_ent, **self.genre_ent, **self.character_ent}
        print("\nEntitites used: ")
        print(self.already_ner_dict)

        return self.original_dialogue_ner_small, self.original_dialogue_ner_full, self.already_ner_dict, \
               facts_ner, attitudes_ner

    # Lot of updating needed for this
    def run_through_logs(self, global_rdr):
        """
            Perform the named entity resolution directly on the logfiles
        """
        path_logs = os.path.join(self.path_logs, self.mturk_session)
        path_data = self.path_data

        if not path_data or not path_logs or not self.mturk_session:
            raise Exception("Missing something.")

        if not global_rdr:
            logs_reader = rdr.ReadLogs(self.path_logs)
        else:
            logs_reader = global_rdr.ReadLogs(self.path_logs)
        # self.list_users, self.list_logtext = logs_reader.run()
        dict_logtext = logs_reader.run()

        mov_ent = ExtractMovieEntity(self.path_data)  # , self.DataMovie, self.DataPerson)
        # Perform the operation for each logfile
        # for _users, _single_logtext in zip(self.list_users, self.list_logtext):
        for logpath, log_info in dict_logtext.items():
            _users = log_info[0]
            single_logtext = log_info[1]
            entities_dict, mov_name = mov_ent.create_dict_of_entities(_users, single_logtext)

            # Would be used to check for variations in movie name during entity resolution
            # For now only perform search if ':' is in movie name. Consider others later e.g ',!'
            self.names_list = []
            if ':' in mov_name:
                self.names_list = self._create_different_searches(mov_name, type="movie", characters="")
            else:
                self.names_list.append(mov_name)

            self.list_US, self.list_UK = None, None
            # Check country and make list for entity resolution search if matching
            if "United States" in entities_dict[1]:
                self.list_US = self._create_different_searches(name="United States", type="country")
            if "United Kingdom" in entities_dict[1]:
                self.list_UK = self._create_different_searches(name="United Kingdom", type="country")

            print("\nEntities in the dict: ")
            print("Person: ")
            print(entities_dict[0])
            print("Info: ")
            print(entities_dict[1])
            print("-----------------------")
            # Perform ner
            curr_userid = 0
            self.found_person_not_in_entities_dict = {}
            dialogue_list = []

            for item in single_logtext:
                if item['type'] == 'text' and item['user']['id'] in _users:
                    if item['user']['id'] == curr_userid:
                        # Update the dialogue_list if the same speaker has used two turns
                        msg = tmp_msg + " [EOU] " + item['msg']
                        # Apply ner here
                        msg_ner = self._implement_resolution(entities_dict, msg)
                        dialogue_list[len(dialogue_list) - 1] = msg_ner
                        tmp_msg = msg
                    else:
                        msg_ner = self._implement_resolution(entities_dict, item['msg'])
                        dialogue_list.append(msg_ner)
                        # tmp_msg is used for when a speaker uses two turns (to put each of them together)
                        tmp_msg = msg_ner
                    curr_userid = item['user']['id']

                    # DEBUG
                    print(dialogue_list[len(dialogue_list) - 1])

            if self.found_person_not_in_entities_dict:
                print('\nPeople not matching from the list of given entities: ')
                print(self.found_person_not_in_entities_dict)
            print(
                ".....................................................................................................")

    def _implement_resolution(self, entities_dict, text, type='None'):
        person_ent_dict, info_ent_dict, character_ent_dict = entities_dict
        # ***********************************************************************
        #    - First implement on movie info,
        #    - then on persons
        #    - and finally on the characters
        # ***********************************************************************

        # check time spent on the individual implementations
        process_text = self._on_info_ent(text, info_ent_dict, type=type)

        # joined_person_ent_dict = {**person_ent_dict, **character_ent_dict}
        # process_text = self._on_person_ent(process_text, joined_person_ent_dict)
        joined_dict_list = [person_ent_dict, character_ent_dict]
        for single_dict in joined_dict_list:
            process_text = self._on_person_ent(process_text, single_dict, type=type)

        # Perform contraction expansion
        # con = contractions.Contractions()
        # process_text = con.expand_contractions(process_text)

        # Perform and tokenization using spacy
        doc = self.nlp(process_text)
        tokenize_spacy = []
        for token in doc:
            tokenize_spacy.append(token.text)
        process_text = " ".join(tokenize_spacy)

        # Put [EOU] back in place
        eou = '[ EOU ]'
        if eou in process_text:
            regex = '\[\sEOU\s\]'
            process_text = re.sub(regex, "[EOU]", process_text)

        # remove empty strings
        msg_list = process_text.split(" ")
        msg_list = list(filter(None, msg_list))
        process_text = " ".join(msg_list)

        return process_text

    def _on_info_ent(self, process_text, info_ent_dict, type=None):
        # *******************************************************************************************************
        #    First perform exact string matching for movie name
        #    Then for cases of single movie name, check if movie name is a Proper noun in the sentence (using spacy)
        #    e.g. Ran
        # *******************************************************************************************************
        for entity, value in info_ent_dict.items():  # entity = movie_name; #value = entity_tag
            if value == 'movie#0':
                # **************************************************
                # Method 1: Exact string match
                # **************************************************
                # USE lower() IF len(movie) > 3
                if len(entity.split(" ")) > 3:
                    if entity.lower() in process_text.lower():
                        found = []
                        regex = entity.lower()
                        matches = re.finditer(regex, process_text.lower(), re.MULTILINE)
                        for matchNum, match in enumerate(matches, start=1):
                            # get position of found match
                            found.append([match.start(), match.end()])
                        if found:
                            for index in found[::-1]:
                                process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]
                            # Update to final entity dict
                            # self.non_actor_ent.update({entity: value})
                            if entity not in self.already_ner_dict:
                                self.already_ner_dict.update({entity: value})

                # Search if movie is a one word name
                elif len(entity.split(" ")) == 1:
                    if entity.lower() in process_text.lower():
                        found = []
                        regex = entity.lower()
                        matches = re.finditer(regex, process_text.lower(), re.MULTILINE)
                        for matchNum, match in enumerate(matches, start=1):
                            # get position of found match
                            # beneficial for one word movie name e.g. meetup 296
                            try:
                                # TODO: include this for other resolutions to improve accuracy
                                if process_text[match.start()-1] == ' ' or process_text[match.start()-1] in string.punctuation or match.start() == 0:
                                    if process_text[match.end()] == ' ' or process_text[match.end()] in string.punctuation or match.end() == len(process_text)+1:
                                        found.append([match.start(), match.end()])
                            # index error for match.end()
                            except IndexError:
                                found.append([match.start(), match.end()])
                        if found:
                            for index in found[::-1]:
                                process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]
                            # Update to final entity dict
                            # self.non_actor_ent.update({entity: value})
                            if entity not in self.already_ner_dict:
                                self.already_ner_dict.update({entity: value})

                elif entity in process_text:
                    # Update to final entity dict
                    # self.non_actor_ent.update({entity: value})
                    if entity not in self.already_ner_dict:
                        self.already_ner_dict.update({entity: value})
                    process_text = re.sub(entity, ' ' + value + ' ', process_text)

                '''
                # PERFROM SEARCH FOR DIFFERENT FORMS OF THE MOVIE NAME
                # Search for the various terms in the list using regex:
                for regex in self.names_list:
                    regex = regex.lower()
                    matches = re.finditer(regex, process_text.lower(), re.MULTILINE)
                    for matchNum, match in enumerate(matches, start=1):
                        match_str = str(match.group())  #match.group() gives result of match                        
                        found = process_text[match.start():match.end()]
                        process_text = re.sub(found, value, process_text)
                '''

                # ****************************************************************************
                # Method 2: Search using lev distance and ngrams for the most similar option:
                # ****************************************************************************
                process_text_list = process_text.split(" ")
                # remove empty strings
                process_text_list = list(filter(None, process_text_list))

                # If only one word utterance, don't perform spacy_ner
                # movies usually not mentioned multiple times in a sentence, so include movie#0 not in text
                if len(process_text_list) > 1 and 'movie#0' not in process_text:
                    most_similar = self._get_max_similarity(self.names_list, process_text, type='movie',
                                                            similarity_measure='lev')
                    if most_similar[0] != "No similarity":
                        matches = re.finditer(most_similar[0], process_text, re.MULTILINE)
                        found = []
                        for matchNum, match in enumerate(matches, start=1):
                            # Use the index to perform substitution
                            found.append([match.start(), match.end()])
                        if found:
                            # Update to final entity dict
                            # self.non_actor_ent.update({entity: value})
                            if entity not in self.already_ner_dict:
                                self.already_ner_dict.update({entity: value})
                            for index in found[::-1]:
                                process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]

                # ********************************************************************
                # Method 3: Spacy 1: Search using spacy and ngrams for the most similar option:
                # ********************************************************************
                # If only one word utterance, don't perform spacy_ner
                if len(process_text_list) > 1 and 'movie#0' not in process_text:
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
                        # self._get_max_similarity(names_list="", sentence="", type="")
                        most_similar, _percentage = self._get_max_similarity(self.names_list, process_text, type='movie',
                                                                             similarity_measure='spacy')
                    # TODO:
                    # Get top two most similar strings and perform Levenshtein distance with that and the movie
                    # name to find the best result
                    # Then subsitute the most similar string
                    if _percentage >= 0.89:
                        # Perform edit distance and jaccard on the spacy result
                        check_list = [most_similar[1]]
                        should_use = self._perform_edit_distance(check_list, most_similar[0], list_type='entity')
                        if should_use[0] != "No match":
                            # .lower() gives different results if removed
                            matches = re.finditer(most_similar[0], process_text, re.MULTILINE)
                            found = []
                            for matchNum, match in enumerate(matches, start=1):
                                # Use the index to perform substitution
                                found.append([match.start(), match.end()])
                            if found:
                                # Update to final entity dict
                                # self.non_actor_ent.update({entity: value})
                                if entity not in self.already_ner_dict:
                                    self.already_ner_dict.update({entity: value})
                                for index in found[::-1]:
                                    process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]

                # ********************************************************************
                # Method 4: Spacy 2: If movie is only one word, perform Pronoun search:
                # ********************************************************************
                if len(entity.split(' ')) == 1 and 'movie#0' not in process_text:
                    # Perform spacy on the text to get proper nouns that match movie name
                    # Load English tokenizer, tagger, parser, NER and word vectors
                    doc = self.nlp(process_text)
                    for _word in doc:
                        if _word.pos_ == 'PROPN':
                            if _word.text == entity:  # 'NOUN', 'PRON'
                                # Update to final entity dict
                                # self.non_actor_ent.update({entity: value})
                                if entity not in self.already_ner_dict:
                                    self.already_ner_dict.update({entity: value})
                                process_text = re.sub(entity, ' ' + value + ' ', process_text)
                            else:
                                # Perform edit distance
                                # Note: This has tendency to bring a lot of False Positives
                                closest_match, ed = self._perform_edit_distance(self.names_list, _word.text,
                                                                                list_type='entity')
                                # If only one word change
                                if closest_match != "No match":
                                    if ed < 2:
                                        matches = re.finditer(closest_match.lower(), process_text.lower(), re.MULTILINE)
                                        found = []
                                        for matchNum, match in enumerate(matches, start=1):
                                            # Use the index to perform substitution
                                            found.append([match.start(), match.end()])
                                        if found:
                                            # Rearrange entity dict
                                            if entity not in self.already_ner_dict:
                                                self.already_ner_dict.update({entity: value})
                                            for index in found[::-1]:
                                                process_text = process_text[:index[0]] + ' ' + value + ' ' \
                                                               + process_text[index[1]:]
                                                # process_text = re.sub(most_similar, value, process_text)
                continue

            if value == 'budget#0':
                # Exact string match
                if entity in process_text:
                    # \\ added for regex metacharacters
                    found_match = "\\" + entity
                    process_text = re.sub(found_match, ' ' + value + ' ', process_text)
                    # Update to final entity dict
                    # self.non_actor_ent.update({entity: value})
                    if entity not in self.already_ner_dict:
                        self.already_ner_dict.update({entity: value})
                    continue

                # Exact string match 2
                entity_2 = entity[1:]
                if entity_2 in process_text:
                    process_text = re.sub(entity_2, ' ' + value + ' ', process_text)
                    # Update to final entity dict
                    # self.non_actor_ent.update({entity: value})
                    if entity not in self.already_ner_dict:
                        self.already_ner_dict.update({entity: value})
                    continue

                # Further check
                # TODO:
                # edit regex for budget to include values less than 1 million
                # regex = r"\$?[0-9]{1,3}[,\s]?\d{3}[,\s]?\d{3}"
                # regex = r"\$?[0-9]{1,3}[,\s]?(\d{3}[,\s]?\d{3}|\b(million)\b)"
                regex = r"\$?[0-9]{1,3}[,\s]?(\d{3}[,\s]?\d{3}|(million|(mil)\b|mill))"
                matches = re.finditer(regex, process_text, re.MULTILINE)
                mill_diff = ['million', 'mil', 'mill']
                for matchNum, match in enumerate(matches, start=1):
                    found_match = str(match.group())  # match.group() gives result of match
                    # Remove dollar sign, commas or spaces if any
                    found_match_edited = re.sub(r"[,\$\s]", '', found_match)
                    # Check if million spelt out and sub
                    for mil_exp in mill_diff:
                        if mil_exp in found_match:
                            found_match_edited = re.sub(mil_exp, '000000', found_match_edited)
                            break
                    # if 'million' in found_match or 'mil' in found_match or 'mill' in found_match :
                        # found_match_edited = re.sub('million', '000000', found_match_edited)
                    # Convert budget and then compare
                    budget_edited = re.sub(r"[,\$\s]", '', entity)
                    if found_match_edited == budget_edited:
                        if '$' == found_match[0]:
                            found_match = "\\" + found_match
                        process_text = re.sub(found_match, ' ' + value + ' ', process_text)
                        # Update to final entity dict
                        # self.non_actor_ent.update({entity: value})
                        if entity not in self.already_ner_dict:
                            self.already_ner_dict.update({entity: value})
                        continue

            if value == 'year#0':
                regex = r"\d{4}"
                matches = re.finditer(regex, process_text, re.MULTILINE)
                for matchNum, match in enumerate(matches, start=1):
                    if int(match.group()) == entity:  # match.group() gives result of match
                        process_text = re.sub(str(match.group()), ' ' + value + ' ', process_text)
                        # Update to final entity dict
                        # self.non_actor_ent.update({str(entity): value})
                        if entity not in self.already_ner_dict:
                            self.already_ner_dict.update({entity: value})
                continue

            if value == 'certificate#0':

                """ # Stricter means for certificate
                perform_cert_resolution = False
                catch_words = ['age', 'restriction', 'rating', 'rated']
                # use iteration to check last two dialogues
                if type == 'small':
                    dialogue_to_check = self.original_dialogue_ner_small
                elif type == 'full':
                    dialogue_to_check = self.original_dialogue_ner_full
                if len(dialogue_to_check) > 1:
                    it = iter(dialogue_to_check[::-1])
                    for last_utt in it:
                        before_last_utt = next(it)
                        for catch_word in catch_words:
                            # also check current utterance
                            if catch_word in last_utt.lower() or catch_word in before_last_utt.lower() or \
                                    catch_word in process_text.lower():
                                perform_cert_resolution = True
                                break
                        break  # forces iteration to only perform search for last two utterances

                if perform_cert_resolution:
                    # TODO: improve the regex
                    regex = r"\s\d{1,2}\s?"  # search for only the exact numbers
                    matches = re.finditer(regex, process_text, re.MULTILINE)
                    found = []
                    for matchNum, match in enumerate(matches, start=1):
                        # get position of found match and remove space if any
                        # try: if there's a space after certificate
                        if process_text[match.end()-1] == ' ':
                            found.append([match.start()+1, match.end()-1])
                        else:
                            # Check if next value is integer
                            # For cases like: cert = 16, and text = 169
                            try:
                                int(process_text[match.end()])
                                break
                            except (ValueError, IndexError):
                                # ValueError: for cases where next value is not an integer
                                # IndexError: for cases where the certificate is the last word
                                found.append([match.start() + 1, match.end()])
                    if found:
                        # start from last index due to string substitutions
                        for index in found[::-1]:
                            if process_text[index[0]:index[1]] == entity:
                                # process_text = re.sub(process_text[index[0]:index[1]], value, process_text)
                                # replace only the found indexes
                                process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]
                                # continue
                                # Update to final entity dict
                                # self.non_actor_ent.update({str(entity): value})
                                if entity not in self.already_ner_dict:
                                    self.already_ner_dict.update({entity: value})
                """

                # Less trict certificate n.e.r
                regex = r"\d{1,2}"  # search for only the exact numbers
                matches = re.finditer(regex, process_text, re.MULTILINE)
                found = []
                for matchNum, match in enumerate(matches, start=1):
                    if process_text[match.start():match.end()] == entity:
                        if process_text[match.start() - 1] == '#':
                            break
                        else:
                            # NOW: try if there's a space before certificate or if it's the starting sentence
                            if process_text[match.start() - 1] == ' ' or match.start() == 0:
                                # and if there's not an int after
                                try:                                    # apparently 0 is not recognized as an int
                                    if int(process_text[match.end()]) or process_text[match.end()] == '0':
                                        break  # if the next character is an integer
                                    else:
                                        found.append([match.start(), match.end()])
                                except (ValueError, IndexError):
                                    # ValueError: for cases where next value is not an integer
                                    # IndexError: for cases where the certificate is the last word
                                    found.append([match.start(), match.end()])
                            # if appears at end of sentence:
                            elif match.end() == len(process_text):
                                try:
                                    if int(process_text[match.start() - 1]) or process_text[match.start()-1] == '0':
                                        break
                                    else:
                                        found.append([match.start(), match.end()])
                                except (ValueError, IndexError):
                                    # ValueError: for cases where prev value is not an integer
                                    # IndexError: for cases where the certificate is the last word
                                    found.append([match.start(), match.end()])
                            # if no space before match.start index and entity is not beginning or end of sentence:
                            else:
                                try:
                                    if int(process_text[match.start() - 1]) or process_text[match.start() - 1] == '0':
                                        break
                                except (ValueError):
                                    # ValueError: for cases where prev value is not an integer
                                    try:
                                        if int(process_text[match.end()]) or process_text[match.end()] == '0':
                                            break
                                        else:
                                            found.append([match.start(), match.end()])
                                    except (ValueError):
                                        found.append([match.start(), match.end()])
                if found:
                    # start from last index due to string substitutions
                    for index in found[::-1]:
                        # double check, probable not necessary
                        process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]
                        # Update to final entity dict
                        # self.non_actor_ent.update({str(entity): value})
                        if entity not in self.already_ner_dict:
                            self.already_ner_dict.update({entity: value})

            if value[0:5] == 'genre':
                if entity.lower() in process_text.lower():
                    regex = entity.lower()
                    matches = re.finditer(regex, process_text.lower(), re.MULTILINE)
                    found = []
                    for matchNum, match in enumerate(matches, start=1):
                        # get position of found match
                        try:
                            # For cases with s: e.g animations... Maybe too specific
                            # Check if next letter after genre is 's', 'ies', 'dramatic'
                            # good = ['s', ' ']
                            # if process_text[match.end()] == good[0]:
                                # found.append([match.start(), match.end()])
                            # Only append if there's a space before the word or the word is the start of the sentence
                            if process_text[match.start()-1] == ' ' or match.start() == 0:
                                found.append([match.start(), match.end()])
                            # For any other case such as space, '.', ...
                            # else:
                                # currently this includes every mention of genre including situations like
                                # 'dramatic', ..., the option to change this is to put them in a 'bad' list
                                # found.append([match.start(), match.end()])
                        except IndexError:
                            found.append([match.start(), match.end()])
                    if found:
                        if entity in self.already_ner_dict:
                            new_value = self.already_ner_dict[entity]
                        else:
                            # new_value = self._get_new_value(entity, value)
                            new_value = self.update_new_value(entity, value)
                        for index in found[::-1]:
                            process_text = process_text[:index[0]] + ' ' + new_value + ' ' + process_text[index[1]:]
                        continue

            if value[0:7] == 'country':
                if entity == 'United States':
                    for regex in self.list_US:
                        found = []
                        matches = re.finditer(regex, process_text, re.MULTILINE)
                        for matchNum, match in enumerate(matches, start=1):
                            if process_text[match.start() - 1] == ' ' or match.start() == 0:
                                # get position of found match
                                found.append([match.start(), match.end()])
                                #found = process_text[match.start():match.end()]
                        if found:
                            for index in found[::-1]:
                                process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]
                            # Update to final entity dict
                            # self.non_actor_ent.update({entity: value})
                            if entity not in self.already_ner_dict:
                                self.already_ner_dict.update({entity: value})
                elif entity == 'United Kingdom':
                    for regex in self.list_UK:
                        found = []
                        matches = re.finditer(regex, process_text, re.MULTILINE)
                        for matchNum, match in enumerate(matches, start=1):
                            if process_text[match.start()-1] == ' ' or match.start() == 0:
                                # get position of found match
                                found.append([match.start(), match.end()])
                                # found = process_text[match.start():match.end()]
                        if found:
                            for index in found[::-1]:
                                process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]
                            # Update to final entity dict
                            # self.non_actor_ent.update({entity: value})
                            if entity not in self.already_ner_dict:
                                self.already_ner_dict.update({entity: value})

                # If country not USA or UK
                elif entity.lower() in process_text.lower():
                    found = []
                    regex = entity.lower()
                    matches = re.finditer(regex, process_text.lower(), re.MULTILINE)
                    for matchNum, match in enumerate(matches, start=1):
                        # get position of found match
                        found.append([match.start(), match.end()])
                    if found:
                        for index in found[::-1]:
                            process_text = process_text[:index[0]] + ' ' + value + ' ' + process_text[index[1]:]
                        # Update to final entity dict
                        # self.non_actor_ent.update({entity: value})
                        if entity not in self.already_ner_dict:
                            self.already_ner_dict.update({entity: value})
                        # continue
        return process_text

    def _on_person_ent(self, process_text, person_ent_dict, type=None):
        # *************************************************
        # Method 1: Perform exact string match for persons
        # *************************************************
        for entity, value in person_ent_dict.items():  # entity = movie_name; #value = entity_tag
            # For person with 3 names
            if len(entity.split(" ")) == 3:
                entity_list = self._create_different_searches(entity, type="person")
                for regex in entity_list:
                    matches = re.finditer(regex.lower(), process_text.lower(), re.MULTILINE)
                    found = []
                    for matchNum, match in enumerate(matches, start=1):
                        # Use the index to perform substitution
                        try:
                            # Check if next letter after name is 's' , '
                            # Maybe redundant
                            good = ['s', "'"]
                            if process_text[match.end()] in good:
                                found.append([match.start(), match.end()])
                            else:
                                found.append([match.start(), match.end()])
                        except IndexError:
                            found.append([match.start(), match.end()])
                    if found:
                        # Rearrange entity dict
                        if entity in self.already_ner_dict:
                            new_value = self.already_ner_dict[entity]
                        else:
                            # new_value = self._get_new_value(entity, value)
                            new_value = self.update_new_value(entity, value)
                        for index in found[::-1]:
                            process_text = process_text[:index[0]] + ' ' + new_value + ' ' + process_text[index[1]:]
                        continue

            elif entity.lower() in process_text.lower():
                if entity in self.already_ner_dict:
                    new_value = self.already_ner_dict[entity]
                else:
                    # new_value = self._get_new_value(entity, value)
                    new_value = self.update_new_value(entity, value)
                process_text = re.sub(entity, ' ' + new_value + ' ', process_text)


        # ************************************************************
        # Method 2: Search using lev distance and ngrams for the most similar option:
        # ************************************************************
        process_text_list = process_text.split(" ")
        # remove empty strings
        process_text_list = list(filter(None, process_text_list))
        # If only one word utterance, don't perform spacy_ner
        if len(process_text_list) > 1:
            most_similar = self._get_max_similarity(person_ent_dict, process_text, type='person',
                                                    similarity_measure='lev')

            if most_similar[0] != "No similarity":
                matches = re.finditer(most_similar[0].lower(), process_text.lower(), re.MULTILINE)
                found = []
                for matchNum, match in enumerate(matches, start=1):
                    # Use the index to perform substitution
                    found.append([match.start(), match.end()])
                if found:
                    # Update to final entity dict
                    if most_similar[1] in self.already_ner_dict:
                        new_value = self.already_ner_dict[most_similar[1]]
                    else:
                        # new_value = self._get_new_value(most_similar[1], person_ent_dict[most_similar[1]])
                        new_value = self.update_new_value(most_similar[1], person_ent_dict[most_similar[1]])
                    for index in found[::-1]:
                        process_text = process_text[:index[0]] + ' ' + new_value + ' ' + process_text[index[1]:]

        # ***********************************************************************
        # Method 3: Spacy 1: spacy and ngrams for the most similar person option:
        # ***********************************************************************
        # If only one word utterance, don't perform spacy_ner
        if len(process_text_list) > 1:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')  # ignore spacy userwarning
                most_similar, _percentage = self._get_max_similarity(person_ent_dict, process_text, type='person',
                                                                     similarity_measure='spacy')
            if _percentage >= 0.89:
                # .lower() gives different results if removed
                # Perform edit distance and jaccard on the spacy result
                check_list = [most_similar[1]]
                should_use = self._perform_edit_distance(check_list, most_similar[0], list_type='entity')
                if should_use[0] != "No match":
                    matches = re.finditer(most_similar[0].lower(), process_text.lower(), re.MULTILINE)
                    found = []
                    for matchNum, match in enumerate(matches, start=1):
                        # Use the index to perform substitution
                        found.append([match.start(), match.end()])
                    if found:
                        # Rearrange entity dict
                        if most_similar[1] in self.already_ner_dict:
                            new_value = self.already_ner_dict[most_similar[1]]
                        else:
                            # new_value = self._get_new_value(most_similar[1], person_ent_dict[most_similar[1]])
                            new_value = self.update_new_value(most_similar[1], person_ent_dict[most_similar[1]])
                        for index in found[::-1]:
                            process_text = process_text[:index[0]] + ' ' + new_value + ' ' + process_text[index[1]:]
                            # process_text = re.sub(most_similar, value, process_text)

        # **********************************************************************
        # Method 4: Spacy 2: spacy for further person matching using POS Tagging
        # **********************************************************************
        _spacy_label = ['PERSON', 'ORG']
        doc = self.nlp(process_text)
        for ent in doc.ents:
            # NOTE: Not all persons found, so search for nouns as well.
            # Also perform exact sring search for names to be sure!
            if ent.label_ in _spacy_label:  # date, ...
                if ent.text != 'EOU':
                    # EXACT MATCH:
                    # If there is only one name
                    if len(ent.text.split()) == 1:
                        possibility = []
                        for entity_, val_ in person_ent_dict.items(): # ['Tim Robbins']
                            entity_split = (entity_.split(" ")) # ['Tim', 'Robbins']
                            for indiv in entity_split:
                                if ent.text.lower() == indiv.lower():
                                    possibility.append(entity_)
                                    break
                        if len(possibility) > 0:
                            if type == 'small':
                                self.printPurple("-- there are {} possibilities for replacing the name {} \n{}".format(
                                                                        len(possibility), ent.text, possibility))
                            elif type == 'full':
                                self.printGreen("-- there are {} possibilities for replacing the name {} \n{}".format(
                                                                        len(possibility), ent.text, possibility))
                            # self.printPurple(possibility)
                            # Substitute for the entity if only one possibility of replacing the name is found
                            if len(possibility) == 1:
                                if possibility[0] in self.already_ner_dict:
                                    new_value = self.already_ner_dict[possibility[0]]
                                else:
                                    # new_value = self._get_new_value(possibility[0], person_ent_dict[possibility[0]])
                                    new_value = self.update_new_value(possibility[0], person_ent_dict[possibility[0]])
                                process_text = re.sub(ent.text, ' ' + new_value + ' ', process_text)
                        elif ent.text not in self.found_person_not_in_entities_dict:
                                self.found_person_not_in_entities_dict.update({ent.text: ent.label_})

                        '''
                        # Only perform changes after searching through actor and character
                        if type == 'character':
                            if len(self.possibility) > 0:
                                self.printPurple("-- there are {} possibilities for replacing the name {} \n{}".format(len(self.possibility),
                                                                                                       ent.text, self.possibility))
                                # self.printPurple(possibility)
                                # Substitute for the entity if only one possibility of replacing the name is found
                                if len(self.possibility) == 1:
                                    new_value = self._get_new_value(self.possibility[0], self.joined_person_ent_dict[self.possibility[0]])
                                    process_text = re.sub(ent.text, ' ' + new_value + ' ', process_text)
                            elif ent.text not in self.found_person_not_in_entities_dict:
                                    self.found_person_not_in_entities_dict.update({ent.text: ent.label_})
                        '''

                    # If length of name more than one, also perform exact search
                    elif ent.text in person_ent_dict:
                        process_text = re.sub(ent.text, ' ' + person_ent_dict[ent.text] + ' ', process_text)

                    # EDIT DISTANCE:
                    # If replace not yet done, Perform edit and jaccard distance
                    # and if not good enough prob, put into found..._dict
                    if ent.text in process_text:
                        res = self._perform_edit_distance(person_ent_dict, ent.text, list_type='entity')
                        if res[0] == "No match":
                            if ent.text not in self.found_person_not_in_entities_dict:
                                self.found_person_not_in_entities_dict.update({ent.text: ent.label_})
                        else:
                            if res[0] in self.already_ner_dict:
                                new_value = self.already_ner_dict[res[0]]
                            else:
                                # new_value = self._get_new_value(res[0], person_ent_dict[res[0]])
                                new_value = self.update_new_value(res[0], person_ent_dict[res[0]])
                            process_text = re.sub(ent.text, ' ' + new_value + ' ', process_text)

        return process_text

    def _get_new_value(self, entity, value):
        # For the new entities dict
        if value[0:5] == 'actor':
            if entity not in self.actor_ent:
                self.actor_ent.update({entity: 'actor#' + str(len(self.actor_ent))})
            return self.actor_ent[entity]
        if value[0:5] == 'genre':
            if entity not in self.genre_ent:
                self.genre_ent.update({entity: 'genre#' + str(len(self.genre_ent))})
            return self.genre_ent[entity]
        if value[0:9] == 'character':
            if entity not in self.character_ent:
                self.character_ent.update({entity: 'character#' + str(len(self.character_ent))})
            return  self.character_ent[entity]
        else:
            self.non_actor_ent.update({entity: value})
            return value

    def update_new_value(self, entity, value):
        # For the new entities dict
        count = 0
        if value[0:5] == 'actor':
            # Get actors in dict and continue count from there
            # if entity in self.already_ner_dict:
                # return self.already_ner_dict[entity]
            # else:
            for key, orig_value in self.already_ner_dict.items():
                if 'actor' in orig_value:
                    count += 1
            new_value = 'actor#' + str(count)
            self.already_ner_dict.update({entity: new_value})
            return new_value
        if value[0:5] == 'genre':
            for key, orig_value in self.already_ner_dict.items():
                if 'genre' in orig_value:
                    count += 1
            new_value = 'genre#' + str(count)
            self.already_ner_dict.update({entity: new_value})
            return new_value
        if value[0:9] == 'character':
            for key, orig_value in self.already_ner_dict.items():
                if 'character' in orig_value:
                    count += 1
            new_value = 'character#' + str(count)
            self.already_ner_dict.update({entity: new_value})
            return new_value
        else:
            self.already_ner_dict.update({entity: value})
            return value

    @staticmethod
    def _create_different_searches(name, type=None, characters=None):
        if type == "movie":
            # FIRST DO FOR JUST MOVIES
            final_list = [name]

            # Split by ':' and delete extra space
            diff_names = []
            for one_name in name.split(":"):
                out = one_name.split(" ")
                out = list(filter(None, out))
                diff_names.append((" ").join(out))

            # Make it one full name
            final_list.append((" ").join(diff_names))   # [Avengers Infinity War]

            # Make this so if ['Avengers'] is a character, don't add it to movie name (e.g. for case of 'Batman')
            # Reverse input order so the entity search is first performed the last name
            for x in diff_names[::-1]:  # ['Infinity War', 'Avengers']
                if x not in characters:
                    final_list.append(x)

            '''
            abbr1 = ""
            abbr2 = ""        
    
            # Abbreviations e.g AIW for Avengers: Infinity War
            # Search for space after ':' and remove
            if ': ' in _name:
                index = _name.find(':')
            char_ = list(name)
            if char_[index+1] == ' ':
                char_.pop(index+1)        
            _name = "".join(char_)
    
            # Split to get abbreviations e.g AIW for Avengers: Infinity War
            for nm_ in diff_names:    
                split_name = nm_.split(' ')   #['Avengers']
                                                #['Infinity', 'War']
                for name_together in split_name:
                    abbr1 += name_together[0]   
    
                if len(split_name) > 2: # e.g: ['Lord', 'of', 'the', 'rings']
                    for name_seperate in split_name:
                        abbr2 += name_seperate[0]   
    
            # Only append abbreviations greater than 2 for now
            #if len(abbr1) > 2:  
                #final_list.append(abbr1)    # AIW (after for loop)
            #if len(abbr2) > 2: # e.g: ['Lord', 'of', 'the', 'rings']
                #final_list.append(abbr2)    # LOTR (after for loop)
            '''
            return final_list

        if type == "country":
            if name == "United States":
                return ["United States", "USA", "U.S.A.", "US", "U.S.", "united states", "usa", "u.s.a.", "u.s."]
            if name == "United Kingdom":
                return ["United Kingdom", "UK", "U.K.", "UK", "united kingdom", "uk", "u.k."]

        if type == "person":
            _name_list = name.split(" ") # ['Paul', 'Thomas', 'Anderson']
            name_0_2 = _name_list[0] + " " + _name_list[2]  # ['Paul Anderson']
            name_1_2 = _name_list[1] + " " + _name_list[2]  # ['Thomas Anderson']
            name_0_1 = _name_list[0] + " " + _name_list[1]  # ['Paul Thomas']
            return  [name, name_0_2, name_1_2, name_0_1]

    def _get_max_similarity(self, names_list, sentence, type=None, similarity_measure=None):
        result_dict = {}
        similarity_lev = {}
        # name_list is used for cases where ":" is in movie name so multiple names created
        # ['Avengers: Infinity War', 'Avengers Infinity War', 'Infinity War', 'Avengers']

        curr_ed = 10
        for name in names_list:
            similarity_dict = {}
            # Split name to check length for ngram
            name_split = name.split(" ")
            # if len name longer than 2, perform multiple ngrams
            # Don't perform 1 grams
            if len(name_split) < 2:
                continue
            elif 1 < len(name_split) < 4:
                _xrange = len(name_split)
            else:
                _xrange = len(name_split) - 1
            _yrange = len(name_split) + 1

            for n in range(_xrange, _yrange):
                ngram_result = self.ngrams_sentence(sentence, n)
                # If len(sentence) < n
                if not ngram_result:
                    continue

                # Check similarity of the movie and the ngrammed phrase
                # ONLY CONVERT TO lower() IF len(movie) > 3
                if similarity_measure == 'spacy':
                    if type=='person':
                        doc1 = self.nlp(name.lower())
                    elif type=='movie':
                        # if len(name.split(" ")) > 3:
                        #     doc1 = self.nlp(name.lower())
                        # else:
                        doc1 = self.nlp(name)
                    for phrase in ngram_result:
                        if type == 'person':
                            doc2 = self.nlp(phrase.lower())
                        elif type == 'movie':
                            # if len(name.split(" ")) > 3:
                            #     doc2 = self.nlp(phrase.lower())
                            doc2 = self.nlp(phrase)
                        similarity = doc1.similarity(doc2)
                        if similarity > 0.85:
                            similarity_dict.update({similarity: [phrase, name]})

                if similarity_measure == 'lev':
                    phrase_chosen, ed = self._perform_edit_distance(ngram_result, name, list_type='ngram')
                    if phrase_chosen != "No match":
                        if ed < curr_ed:  # only update for edit distances less than or = 5
                            similarity_lev.update({name: [phrase_chosen, ed]})
                            curr_ed = ed

            if similarity_dict:
                single_max_result = max(key for key in similarity_dict.keys())
                result_dict.update({single_max_result : similarity_dict[single_max_result]})

        # Get the most likely possibility
        if similarity_measure == 'spacy':
            if result_dict:
                # min_val = min(key for key in result_dict.keys())
                # if all max probs are equal, use the longest as the most likely
                tmp_prob = 0
                # tmp_len = 0
                same = False
                for prob, components in result_dict.items():
                    '''
                    if min_val >= 0.90:
                        # Pick the longest result as the most probable one:
                        sent = result_dict[0][2]
                        name__ = result_dict[0][1]
                        pb_ = result_dict[0]
                        return [[sent, name__],pb_]
                    '''
                    if prob == tmp_prob:
                        same = True
                    tmp_prob = prob
                if same is True:
                    curr_len = 0
                    for single_prob in result_dict:
                        # Check if the phrases are the same length, if so then probably the same phrase
                        if len(result_dict[single_prob][0]) > curr_len:
                            single_phrase = result_dict[single_prob][0]
                            _name = result_dict[single_prob][1]
                            pb = single_prob
                            curr_len = len(single_phrase)
                    # return the longest phrase as the most probable
                    return [single_phrase, _name], pb
                # else return the max
                else:
                    try:
                        best_possibility = max(key for key in similarity_dict.keys())
                        return similarity_dict[best_possibility], best_possibility
                        # TODO: Debug this error
                    except ValueError:
                        return ["No similarity", ""], 0.0
            else:
                return ["No similarity", ""], 0.0

        if similarity_measure == 'lev':
            if len(similarity_lev) == 1:
                # similarity_lev.update({Robert D. San Souci: ['robert san souchi as': 7]})
                for name_, info in similarity_lev.items():
                    return [info[0], name_]
                '''
                # if multiple similarity_lev, choose the one with the min edit distance
                min_ed = min(value[1] for value in similarity_lev.values())
                for name_, info in similarity_lev.items():
                    if info[1] == min_ed:
                        return [info[0], name_]
                '''
            elif len(similarity_lev) > 1:
                curr_len = 0
                for name__, info in similarity_lev.items():
                    # Choose the one with the longest length
                    if len(name__) >= curr_len:
                        _selected_phrase = info[0]
                        if type == 'movie':
                            ent = names_list[0]
                        if type == 'person':
                            ent = name__
                        curr_len = len(name__)
                return [_selected_phrase, ent]
            else:
                return ["No similarity", ""]

    @staticmethod
    def _perform_edit_distance(check_list, name, list_type=None):
        # TODO: Maybe to improve accuracy, before performing edit distance, remove space and punctuations
        dist_dict = {}
        for single_entity in check_list:
            _ed = edit_distance(name.lower(), single_entity.lower())  # Edit distance
            _jd = jaccard_distance(set(name.lower()), set(single_entity.lower()))  # Jaccard distance
            dist_dict.update({single_entity: [_ed, _jd]})

        res_threshold = {}
        for entity, distances in dist_dict.items():
            ed_ = distances[0]
            jd_ = distances[1]
            # TODO: Try remove threshold and pick the best possibility (min)
            # Threshold for the edit distance and jaccard distance

            if list_type == 'ngram':
                if len(name.split(" ")) < 4:
                    if ed_ < 3 and jd_ < 0.3:
                        res_threshold.update({entity: distances})
                # Less punishment for longer movie or person names in the sentence
                else:
                    if ed_ < 4 and jd_ < 0.3:
                        res_threshold.update({entity: distances})

            if list_type == 'entity':
                # Less punishment for longer movie or person names
                if len(entity.split(" ")) > 3:
                    if ed_ < 3 and jd_ < 0.2:
                        res_threshold.update({entity: distances})
                else:
                    if ed_ < 3 and jd_ < 0.3:
                        res_threshold.update({entity: distances})

        if len(res_threshold) == 1:
            for closest_match, dist in res_threshold.items():
                return closest_match, dist[0]
        elif not res_threshold:
            return "No match", ""
        else:
            # If more than one result below the threshold, then pick the min edit distance
            min_ed = min(value[0] for value in res_threshold.values())
            # min_jd = min(value[1] for value in res_threshold.values())
            for closest_match, value in res_threshold.items():
                if value[0] == min_ed:
                    return closest_match, value[0]

    def ngrams_sentence(self, sent, n):
        '''
        # Tokenize 2: Using spacy
        doc = self.nlp(sent.lower())
        tokens = []
        for token in doc:
            tokens.append(token.text)
        '''

        # Future implementation perhaps
        '''
        # Tokenize: nltk whitespace tok with indexing
        tokens = WhitespaceTokenizer().tokenize(sent)
        span_generator = WhitespaceTokenizer().span_tokenize(sent)
        spans = [span for span in span_generator]

        # Concatenate tokens and use the zip function to help generate n-grams
        sequence = [tokens[i:] for i in range(n)]
        index = [spans[i:] for i in range(n)]

        # The zip function takes the sequences as a list of inputs (using the * operator,
        ngrams__ = zip(*sequence)
        ngram_res = [" ".join(ngram) for ngram in ngrams__]
        index_gram = zip(*index)
        index_gram_res = [i_ngram for i_ngram in index_gram]
        final_res = {}
        for x, y in zip(ngram_res, index_gram_res):
            final_res.update({x: [y[0][0], y[len(y)-1][1]]})

        return final_res
        '''

        # Tokenize: nltk word_tok
        tokens = word_tokenize(sent)#.lower())
        # Concatenate tokens and use the zip function to help generate n-grams
        sequence = [tokens[i:] for i in range(n)]
        # The zip function takes the sequences as a list of inputs (using the * operator,
        ngrams = zip(*sequence)
        return [" ".join(ngram) for ngram in ngrams]


    # for DEBUG
    @staticmethod
    def printPurple(skk):
        print("\033[95m{}\033[00m".format(skk))

    @staticmethod
    def printGreen(skk):
        print("\033[92m{}\033[00m".format(skk))

if __name__ == "__main__":
    import reader as rdr
    from libs.moviedatalib import DataMovie, DataPerson, Trivia

    path_logs = "../logfiles/"
    mturk_session = "moviedatagen_real_test_2/"  # "versuchsreihe3/"
    path_data = "./movies/data.pkl"

    ner = NamedEntityResolution(path_logs, mturk_session, path_data)
    # ner = NamedEntityResolution(path_logs="", mturk_session=mturk_session)
    # ner.run("")