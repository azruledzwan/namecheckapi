"""
This module is used to extract excerpts of job requirements from a given job description.
"""
from dataclasses import replace
import re

from thefuzz import fuzz


class NameMatcher:
    """
    NameMatcher class
    """

    suffixes = {"junior", "jr", "senior", "sr", "ii", "iii", "iv"}
    weight_order = ["first_names", "last_name", "suffix"]
    salutations = {"encik", "cik", "tuan", "puan", "mr", "mrs", "miss", "ms"}
    bad_bank = ["PBB0233", "MB2U0227"]
    # substitute = {'bte','binti','bt'}

    def _compare(self, str1, str2):
        """
        Implements string comparison algorithm between 2 strings
        """
        #fuzz.ratio() must exact match of two input strings
        #fuzz.partial_ratio() takes in the shortest string
        #fuzz.token_sort_ratio Attempts to account for similar strings out of order.
        #fuzz.token_set_ratio considers duplicate words as a single word.
        return fuzz.ratio(str1, str2)

    def match_names(
        self, name1, name2, acc_uuid, buyer_bank_id="Other"
    ):
        """
        ## Description
        Matches the two names by first removing the salutations.

        ## Input Params
        name1: Name from IC
        name2: Name from other bank
        buyer_bank_id: Optional. If not specified, default to others.
        """
        
        # remove trailing spaces and convert to uppercase
        name1 = name1.strip().upper()
        name2 = name2.strip().upper()
        print(name1)
        print(name2)

        compare = self._compare(name1, name2)
        print(compare)
        if compare == 100:
            return compare
        
        buyer_name_len = len(name2)

        # remove salutations
        name1 = self._remove_salut(name1)
        name2 = self._remove_salut(name2)
        print(name1)
        print(name2)
        # if name_dict2 is from bad_bank, then truncate length of name_dict1.
        if buyer_bank_id.upper() in self.bad_bank:
            name1 = name1[: len(name2)]

        # if buyer_name_len is 40, then the actual name might have been truncated.
        # once we have removed salutation, consider truncating the name1
        # based on the new length of name2
        if buyer_name_len == 40:
            name1 = name1[: len(name2)]

        compare = self._compare(name1, name2)
        print(compare)
        if compare == 100:
            return compare
        else: 
            name1 = self._prefix_match(name1)
            name2 = self._prefix_match(name2)
            print(name1)
            print(name2)
            
        return self._compare(name1, name2)

    def _remove_salut(self, name):
        """Remove salutations from name."""
        first_tok = re.split("[\s,]", name)[0]
        if first_tok.lower().replace(".", "") in self.salutations:
            name = name[len(first_tok) :].strip()
        return name

    def _prefix_match(self, name):
        if ' BINTI ' in name:
            name  = name.replace('BINTI', 'BT')
            return name
        if ' BTE ' in name:
            name  = name.replace('BTE', 'BT')
            return name
        return name