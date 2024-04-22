import ratemyprofessor
from datetime import datetime
import json


list = open('../cs-instructors.txt', 'r').read().split('\n')
print(list)


uiuc = ratemyprofessor.get_school_by_name("University of Illinois Urbana-Champaign")
cleaned = []
for instructor in list:
    [last, first] = instructor.split(',')
    # Alawini, Abdussalam A -> Abdussalam Alawini
    first = first.strip().split(' ')[0]
    name = f'{first} {last}'
    cleaned += [name]

try:
    dataset = json.load(open('saved-ratings.json', 'r'))
except FileNotFoundError:
    dataset = {}
except json.decoder.JSONDecodeError:
    dataset = {}
for name in cleaned:
    if name in dataset:
        print(name, ' already loaded')
        continue
    res = ratemyprofessor.get_professor_by_school_and_name(uiuc, name)
    if res:
        data = {
            'rating': res.rating,
            'difficulty': res.difficulty,
            'would_take_again': res.would_take_again,
            'num_ratings': res.num_ratings,
            'department': res.department,
            'name': res.name,
        }
        props = ['rating', 'difficulty', 'comment','class_name', 'date', 'take_again', 'grade', 'thumbs_up', 'thumbs_down', 'online_class', 'credit', 'attendance_mandatory']
        ratings = res.get_ratings()
        json_ratings = [{prop: str(getattr(rating, prop)) if type(getattr(rating, prop)) == datetime else getattr(rating, prop) for prop in props} for rating in ratings]
        data['ratings'] = json_ratings
        dataset[res.name] = data
        print('Saved', name)
        with open('saved-ratings.json', 'w') as outfile:
            json.dump(dataset, outfile)
    else:
        print('No results for professor', name)
