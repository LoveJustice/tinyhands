import datetime
import pytz
from django.core.exceptions import ObjectDoesNotExist

from dataentry.models import MatchAction, MatchHistory, MatchType, Person, PersonMatch

import id_matching.link_records as lnk
import id_matching.predict_matches as pm

def update_matches(id, persons_to_match, classifier, stats):
    notes = 'Automated suggested match'
    match_can = lnk.get_match_can_for_single(id, persons_to_match)
    match_can_df = lnk.eval_match_can(match_can, persons_to_match)
    match_can_df = lnk.adjust_scores(match_can_df, 'Phone', 0.6)
    #print('update_match', id, len(match_can_df))
    match_can_p = pm.get_predictions(match_can_df, classifier)
    possible_matches = pm.get_top_matches(match_can_p, persons_to_match)
    person1 = Person.objects.get(id=id)
    tz = pytz.timezone('UTC')
    if possible_matches is not None:
        suggested_match = MatchType.objects.get(name="Suggested")
        create_match = MatchAction.objects.get(name="create match")
        
        for idx in range(0, len(possible_matches)):
            id1 = possible_matches.iloc[idx]['id1']
            id2 = possible_matches.iloc[idx]['id2']
            person2 = Person.objects.get(id=id2)
            #print ('pair', person1.id, person2.id, person1.master_person.id, person2.master_person.id)
            if person1.master_person != person2.master_person:
                try:
                    person_match = PersonMatch.objects.get(master1=person1.master_person, master2=person2.master_person)
                    stats['existing_match'] += 1
                except:
                    try:
                        person_match = PersonMatch.objects.get(master1=person2.master_person, master2=person1.master_person)
                        stats['existing_match'] += 1
                    except:
                        person_match = PersonMatch()
                        person_match.master1 = person1.master_person
                        person_match.master2 = person2.master_person
                        person_match.match_type = suggested_match
                        person_match.notes = notes
                        person_match.match_results = {
                            'Match_Prob':str(possible_matches.iloc[idx]['Match_Prob']),
                            'Form Number':str(possible_matches.iloc[idx]['Form Number']),
                            'Form':str(possible_matches.iloc[idx]['Form']),
                            'Name Match':str(possible_matches.iloc[idx]['Name Match']),
                            'Phonetic Name Match':str(possible_matches.iloc[idx]['Phonetic Name Match']),
                            'Phone Match':str(possible_matches.iloc[idx]['Phone Match']),
                            'Social Media Match':str(possible_matches.iloc[idx]['Social Media Match']),
                            }
                        person_match.save()
                        
                        match_history = MatchHistory()
                        match_history.master1 = person1.master_person
                        match_history.master2 = person2.master_person
                        match_history.match_type = suggested_match
                        match_history.action = create_match
                        match_history.notes = notes
                        match_history.match_results = person_match.match_results
                        match_history.save()
                        stats['new_match'] += 1
            else:
                stats['existing_match'] += 1
    
    person1.last_match_time = datetime.datetime.now().astimezone(tz) + datetime.timedelta(minutes=1)
    person1.save()
    