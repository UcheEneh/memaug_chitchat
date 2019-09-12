import time
import os

# This file should be able to start the whole postprocessing.

# from sources import named_entity_resolution as ner
# from sources import process_logs as plog
# from sources import visualizer as vis
from sources import reader as global_rdr
from sources import process_logs
# from sources import new_movies as nm

from sources import fix_facts_ner

# from libs.moviedatalib import DataMovie, DataPerson

def printGreenBackground(skk):
    print("\033[102m{}\033[00m".format(skk))

if __name__ == "__main__":
    # mturk_session= "check_problematic"
    mturk_session = "large_dataset"
    
    # ner_obj = ner.NamedEntityResolution()
    # ner_obj.run()
    # print("DEBUG")
    #
    # vis_obj = vis.Visualizer(path_logs="./logfiles/", mturk_session="dc_1_tmp")
    # vis_obj.run(global_rdr)
    
    # plog_obj = plog.ProcessLogs(path_logs="./logfiles/", mturk_session=mturk_session)
    # plog_obj.run(global_rdr)
    
    # nm_obj = nm.NewMovies(path='./movies/', txt='full movies list.txt')
    # nm_obj.run()
    
    # gmd_obj = gmd.MovieDataGen(DataMovie, DataPerson)
    # gmd_obj.generate_test_corpus()

    # Fabian
    '''
    processor = process_logs.ProcessLogs(path_logs="logfiles/dataset/logfiles", mturk_session="logfiles",
                                         path_stories="logfiles/dataset/stories_prepared.pkl",
                                         path_data="logfiles/dataset/data_with_used_trivia.pkl")
    processor.run(global_rdr=global_rdr)
    '''

    # Uche

    start = time.time()
    processor = process_logs.ProcessLogs(path_logs="logfiles", mturk_session=mturk_session,
                                         path_stories="movies/stories_prepared.pkl",
                                         path_data="movies/data_with_used_trivia.pkl")
    processor.run(global_rdr=global_rdr)
    end = time.time()

    '''
    # start = time.time()
    fix_ = fix_facts_ner.FixFacts_NER(path_json=os.path.join("logfiles/output/", mturk_session, "healthy"),
                                           path_data="movies/data_with_used_trivia.pkl")
    dicts_given = [processor.result, processor.entities_dict_full]
    fix_.run(global_rdr=global_rdr, dicts_given=dicts_given)
    # end = time.time()
    '''

    printGreenBackground("Processing time of complete logs: {0:.4f} secs".format(end - start))
    printGreenBackground("--------------------------------: {0:.3f} mins".format((end - start) / 60))