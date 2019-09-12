"""
Fix named entity resolution in processed dialogue Facts subject

"""
import os
import pickle
import copy
import re
import string

import json
import shutil

# from libs import moviedatalib
from sources import named_entity_resolution as ner

def printPurple(skk):
    print("\033[95m{}\033[00m".format(skk))
def printRed(skk):
    print("\033[91m{}\033[00m".format(skk))
def printGreen(skk):
    print("\033[92m{}\033[00m".format(skk))
def printCyan(skk):
    print("\033[96m{}\033[00m".format(skk))
def printGreenBackground(skk):
    print("\033[102m{}\033[00m".format(skk))


class FixFacts_NER:
    def __init__(self, path_json, path_data):
        self.path_json = path_json
        self.movie_data = pickle.load(file=open(path_data, 'rb'))
        self.ner = ner.NamedEntityResolution(path_data=self.movie_data, )

    def run(self, global_rdr, dicts_given=None):
        if dicts_given is None:
            if not global_rdr:
                logs_reader = rdr.ReadLogs(self.path_json)
            else:
                logs_reader = global_rdr.ReadLogs(self.path_json)
            dict_logtext = logs_reader.run(type="fix")
            mov_ent = ner.ExtractMovieEntity(self.movie_data, already_loaded=True)
        else:
            dict_logtext = {}
            [result, entities_dict] = dicts_given
            full_ent_dict = [entities_dict[1], entities_dict[0], entities_dict[2]]
            dict_logtext.update({0:result})

        num_logs = len(dict_logtext)
        for cnt, item in enumerate(dict_logtext.values(), start=1):
            print("\nFixing log {} / {}".format(cnt, num_logs))

            if dicts_given is None:
                # Get movie name
                if item["story"][2]["story_type"] == 'PersonToMovieStory':
                    movie_title = item["story"][0]["entities"][2]
                else:
                    movie_title = item["story"][0]["entities"][0]
                logname_split = item["log_file_name"].split("-")
                for x in logname_split[::-1]:
                    meetup_name = x
                    break
                logfile_info = [movie_title, meetup_name]
                entities_dict, mov_name = mov_ent.create_dict_of_entities(logfile_info=logfile_info)
                full_ent_dict = [entities_dict[1], entities_dict[0], entities_dict[2]]


            # ****************************************************
            # Perform facts and attitudes named entity resolution
            # ****************************************************
            # FACTS
            facts_relations = {'has_writer': "writer",
                               'has_director': "director",
                               'has_actor': "actor",
                               'has_release_year': "year",
                               'has_shot_location': "country",
                               'has_budget': "budget",
                               'has_age_certificate': "certificate",
                               'has_genre': "genre"}

            self.already_ner_dict = item['named_entity_dict']
            # self.already_ner_rev = dict(zip(self.already_ner_dict.values(), self.already_ner_dict.keys()))

            fix_fact = False
            fix_att = False
            # Loop through each speaker and their facts
            printPurple("---------Original")
            printGreen("Facts")

            # regex_metacharacters = ['$', '?', '+', '*']
            for speaker, full_triple in item["facts"].items():
                # Assuming single speaker has multiple facts given, therefore multiple triples:
                print(speaker)
                for single_triple in full_triple:
                    print(single_triple)
                    # Facts table entity
                    for single_ent_dict in full_ent_dict:
                        ############################
                        # FACTS SUBJECT
                        ############################
                        _subject = single_triple['subject']
                        if single_triple['subject'] in single_ent_dict:
                            if _subject in self.already_ner_dict:
                                value = self.already_ner_dict[_subject]
                            else:
                                value = self.update_new_value(_subject, single_ent_dict[_subject])
                            single_triple['subject'] = single_triple['subject'].replace(_subject, value)
                            fix_fact = True

                        if "?" in single_triple['subject']:
                            single_triple['subject'] = single_triple['subject'].replace("?", '')

                        ############################
                        # FACTS OBJECT
                        ############################
                        # Facts table value
                        # For now don't include certificate for trivia and plot
                        for ent, val in single_ent_dict.items():
                            if single_triple['relation'] == 'has_age_certificate':
                                # Only use certificate for has_certificate relation
                                ent = str(ent)
                            else:
                                if val == 'certificate':
                                    continue
                                else:
                                    ent = str(ent)
                            if ent in single_triple['object']:  # in final_ent_dict:
                                if ent in self.already_ner_dict:
                                    value = self.already_ner_dict[ent]
                                else:
                                    if val == 'year':
                                        ent_ = int(ent)
                                    else:
                                        ent_ = ent
                                    value = self.update_new_value(ent_, single_ent_dict[ent_])
                                single_triple['object'] = single_triple['object'].replace(ent, value)
                                fix_fact = True
                                # continue

            # ATTITUDES
            # attitudes_relations not necessary since entity resolution only performed on 'subject'
            printCyan("\nAttitudes")
            # Loop through each speaker
            for speaker, full_triple in item["attitudes"].items():
                print(speaker)
                # Assuming single speaker has multiple attitudes given, therefore multiple triples:
                for single_triple in full_triple:
                    print(single_triple)
                    for single_ent_dict in full_ent_dict:
                        ############################
                        # ATTITUDE SUBJECT
                        ############################
                        # Attitudes table entity
                        _subject = single_triple['subject']
                        # convert to string
                        if _subject in single_ent_dict:
                            if _subject in self.already_ner_dict:
                                value = self.already_ner_dict[_subject]
                            else:
                                if single_ent_dict[_subject][0:4] == 'year':
                                    _subject_ = int(_subject)
                                else:
                                    _subject_ = _subject
                                value = self.update_new_value(_subject_, single_ent_dict[_subject_])
                                # single_triple['subject'] = re.sub(repr(_subject), value, single_triple['subject'])
                            single_triple['subject'] = single_triple['subject'].replace(_subject, value)
                            fix_att = True
                            # continue
                        if "?" in single_triple['subject']:
                            single_triple['subject'] = single_triple['subject'].replace("?", '')

            print("\n")
            printPurple("\n---------After Fix: ")
            printGreen("Facts")
            for speaker, full_triple in item['facts'].items():
                # Assuming single speaker has multiple facts given, therefore multiple triples:
                print(speaker)
                for single_triple in full_triple:
                    if fix_fact:
                        printRed(single_triple)
                    else:
                        print(single_triple)

            printCyan("\nAttitudes")
            for speaker, full_triple in item['attitudes'].items():
                print(speaker)
                # Assuming single speaker has multiple attitudes given, therefore multiple triples:
                for single_triple in full_triple:
                    if fix_att:
                        printRed(single_triple)
                    else:
                        print(single_triple)

            print("\n")
            print('Entity Dict:')
            printGreenBackground(item['named_entity_dict'])
            # printGreenBackground("================================================================="
            #                     "======================================================")

            # Save new log
            self._save(item, item['log_file_name'], 'reedited')

            # Move already processed logs to new folder
            src = os.path.join(self.path_json, item["log_file_name"] + '.txt')
            if not os.path.exists(os.path.join(self.path_json, 'done')):
                os.makedirs(os.path.join(self.path_json, 'done'))
            dst = os.path.join(self.path_json, 'done', item["log_file_name"] + '.txt')
            shutil.move(src, dst)

    def update_new_value(self, entity, value):
        # For the new entities dict
        count = 0
        if value[0:5] == 'actor':
            # Get actors in dict and continue count from there
            for key, orig_value in self.already_ner_dict.items():
                if 'actor' in orig_value:
                    count += 1
            new_value = 'actor#' + str(count)
            self.already_ner_dict.update({entity: new_value})
            return new_value
        if value[0:5] == 'genre':
            # Get actors in dict and continue count from there
            for key, orig_value in self.already_ner_dict.items():
                if 'genre' in orig_value:
                    count += 1
            new_value = 'genre#' + str(count)
            self.already_ner_dict.update({entity: new_value})
            return new_value
        if value[0:9] == 'character':
            # Get actors in dict and continue count from there
            for key, orig_value in self.already_ner_dict.items():
                if 'character' in orig_value:
                    count += 1
            new_value = 'character#' + str(count)
            self.already_ner_dict.update({entity: new_value})
            return new_value
        else:
            self.already_ner_dict.update({entity: value})
            return value

    def _save(self, result, filename, subfolder=""):
        if not os.path.exists(os.path.join(self.path_json, subfolder)):
            os.makedirs(os.path.join(self.path_json, subfolder))
        # Save as json
        with open(os.path.join(self.path_json, subfolder, filename + '.txt'), 'w') as outfile:
            json.dump(result, outfile)



if __name__ == '__main__':
    import reader as rdr