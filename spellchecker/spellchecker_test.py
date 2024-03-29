from __future__ import division, unicode_literals

""" Unit test """

import unittest
import os

from spellchecker import SpellChecker

class TestSpellChecker(unittest.TestCase):
    
    
    def test_correction(self):
        spell = SpellChecker(language='en')
        
        self.assertEqual(spell.correction('ths'), 'the')
        self.assertEqual(spell.correction('ergo'), 'ergo')
        self.assertEqual(spell.correction('alot'), 'a lot')
        self.assertEqual(spell.correction('this'), 'this')
        self.assertEqual(spell.correction('-'), '-')
        self.assertEqual(spell.correction('1213'), '1213')
        self.assertEqual(spell.correction('1213.9'), '1213.9')
    
    def test_suggestions(self):
        ''' test spell checker suggestions '''
        spell = SpellChecker(language='en')
        cands = {'tes', 'tps', 'th', 'thi', 'tvs', 'tds', 'tbs', 'bhs', 'thf',
                 'chs', 'tis', 'thes', 'tls', 'tho', 'thu', 'thr', 'dhs',
                 "th'", 'thus', 'ts', 'ehs', 'tas', 'ahs', 'thos', 'thy',
                 'tcs', 'nhs', 'the', 'tss', 'hs', 'lhs', 'vhs', "t's", 'tha',
                 'whs', 'ghs', 'rhs', 'this'}
        self.assertEqual(spell.suggestions('ths'), cands)
        self.assertEqual(spell.suggestions('the'), {'the'})
        self.assertEqual(spell.suggestions('-'), {'-'})
        
    def test_words(self):
        ''' test the parsing of words '''
        spell = SpellChecker(language='en')
        res = ['this', 'is', 'a', 'test', 'of', 'this']
        self.assertEqual(spell.split_words('This is a test of this'), res)
    
    """
    def test_load_external_dictionary(self):
        ''' test loading a local dictionary '''
        here = os.path.dirname(__file__)
        filepath = '{}/resources/small_dictionary.json'.format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath)
        self.assertEqual(spell['a'], 1)
        self.assertTrue('apple' in spell)
    
        
    def test_load_text_file(self):
        ''' test loading a text file '''
        here = os.path.dirname(__file__)
        filepath = '{}/resources/small_doc.txt'.format(here)
        spell = SpellChecker(language=None)  # just from this doc!
        spell.word_frequency.load_text_file(filepath)
        self.assertEqual(spell['a'], 3)
        self.assertEqual(spell['storm'], 2)
        self.assertFalse('awesome' in spell)
        self.assertTrue(spell['whale'])
        self.assertTrue('waves' in spell)
    
    def test_word_probability(self):
        ''' test the word probability calculation '''
        spell = SpellChecker(language='en')
        # if the default load changes so will this...
        num = spell.word_frequency['the']
        denom = spell.word_frequency.total_words
        self.assertEqual(spell.word_probability('the'), num / denom)

    def test_word_known(self):
        ''' test if the word is a `known` word or not '''
        spell = SpellChecker(language='en')
        self.assertEqual(spell.known(['this']), {'this'})
        self.assertEqual(spell.known(['sherlock']), {'sherlock'})
        self.assertEqual(spell.known(['holmes']), {'holmes'})
        self.assertEqual(spell.known(['known']), {'known'})
        self.assertEqual(spell.known(['-']), {'-'})

        self.assertEqual(spell.known(['foobar']), set())
        self.assertEqual(spell.known(['ths']), set())
        self.assertEqual(spell.known(['ergos']), set())

    def test_unknown_words(self):
        ''' test the unknown word functionality '''
        spell = SpellChecker(language='en')
        self.assertEqual(spell.unknown(['this']), set())
        self.assertEqual(spell.unknown(['sherlock']), set())
        self.assertEqual(spell.unknown(['holmes']), set())
        self.assertEqual(spell.unknown(['known']), set())
        self.assertEqual(spell.unknown(['-']), set())

        self.assertEqual(spell.unknown(['foobar']), {'foobar'})
        self.assertEqual(spell.unknown(['ths']), {'ths'})
        self.assertEqual(spell.unknown(['ergos']), {'ergos'})

    def test_word_in(self):
        ''' test the use of the `in` operator '''
        spell = SpellChecker(language='en')
        self.assertTrue('key' in spell)
        self.assertFalse('rando' in spell)

    def test_word_contains(self):
        ''' test the contains functionality '''
        spell = SpellChecker(language='en')
        self.assertEqual(spell['the'], 6187925) 
    
    def test_edit_distance_one(self):
        ''' test a case where edit distance must be one '''
        here = os.path.dirname(__file__)
        filepath = '{}/resources/small_dictionary.json'.format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath, distance=1)
        self.assertEqual(spell.suggestions('hike'), {'bike'})

    def test_edit_distance_one_property(self):
        ''' check the property setting of the distance property '''
        spell = SpellChecker(language='en', distance=1)
        self.assertEqual(spell.distance, 1)
        spell.distance = 2
        self.assertEqual(spell.distance, 2)

    def test_edit_distance_invalud(self):
        ''' check the property setting of the distance property on invalid inputs '''
        spell = SpellChecker(language='en', distance=None)
        self.assertEqual(spell.distance, 2)
        spell.distance = 1
        self.assertEqual(spell.distance, 1)
        spell.distance = 'string'
        self.assertEqual(spell.distance, 2)

    def test_edit_distance_two(self):
        ''' test a case where edit distance must be two '''
        here = os.path.dirname(__file__)
        filepath = '{}/resources/small_dictionary.json'.format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath)
        self.assertEqual(spell.suggestions('ale'), {'a', 'apple'})
        
    def test_remove_words(self):
        ''' test is a word is removed '''
        spell = SpellChecker(language='en')
        self.assertEqual(spell['the'], 6187925)
        spell.word_frequency.remove_words(['the'])
        self.assertEqual(spell['the'], 0)

    def test_remove_word(self):
        ''' test a single word removed '''
        spell = SpellChecker(language='en')
        self.assertEqual(spell['teh'], 6)
        spell.word_frequency.remove('teh')
        self.assertEqual(spell['teh'], 0)

    def test_remove_by_threshold(self):
        ''' test removing everything below a certain threshold '''
        spell = SpellChecker(language='en')
        cnt = 0
        for key in spell.word_frequency.keys():
            if spell.word_frequency[key] < 7:
                cnt += 1
        self.assertGreater(cnt, 0)
        spell.word_frequency.remove_by_threshold(7)
        cnt = 0
        for key in spell.word_frequency.words():  # synonym for keys
            if spell.word_frequency[key] < 7:
                cnt += 1
        self.assertEqual(cnt, 0)

    def test_add_word(self):
        ''' test adding a word '''
        spell = SpellChecker(language='en')
        self.assertEqual(spell['meh'], 0)
        spell.word_frequency.add('meh')
        self.assertEqual(spell['meh'], 1)

    def test_checking_odd_word(self):
        ''' test checking a word that is really a number '''
        spell = SpellChecker(language='en')
        self.assertEqual(spell.edit_distance_1('12345'), {'12345'})

    def test_unique_words(self):
        ''' test the unique word count '''
        spell = SpellChecker(language='en')
        self.assertEqual(spell.word_frequency.unique_words, len(list(spell.word_frequency.keys())))

    def test_capitalization(self):
        ''' test that capitalization doesn't affect in comparisons '''
        spell = SpellChecker(language=None)
        spell.word_frequency.add('Bob')
        spell.word_frequency.add('Bob')
        spell.word_frequency.add('Bab')
        self.assertEqual('Bob' in spell, True)
        self.assertEqual('BOb' in spell, True)
        self.assertEqual('BOB' in spell, True)
        self.assertEqual('bob' in spell, True)

        words = ['Bb', 'bb', 'BB']
        self.assertEqual(spell.unknown(words), {'bb'})

        known_words = ['BOB', 'bOb']
        self.assertEqual(spell.known(known_words), {'bob'})

        self.assertEqual(spell.suggestions('BB'), {'bob', 'bab'})
        self.assertEqual(spell.correction('BB'), 'bob')

    def test_pop(self):
        ''' test the popping of a word '''
        spell = SpellChecker(language='en')
        self.assertEqual('apple' in spell, True)
        self.assertGreater(spell.word_frequency.pop('apple'), 1)
        self.assertEqual('apple' in spell, False)

    def test_pop_default(self):
        ''' test the default value being set for popping a word '''
        spell = SpellChecker(language='en')
        self.assertEqual('appleies' in spell, False)
        self.assertEqual(spell.word_frequency.pop('appleies', False), False)
    """
         
if __name__ == "__main__":
    unittest.main()