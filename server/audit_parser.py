from bs4 import BeautifulSoup
from bs4.element import Tag
import re

SPECIAL_TOPICS = {
    'ADV': [400, 490],
    'ANTH': [499],
    'ARTD': [499],
    'ARTS': [445],
    'CHLH': [494],
    'CI': [499],
    'CMN': [396, 496],
    'CPSC': [499],
    'CS': [498],
    'DANC': [451],
    'ECE': [498],
    'ENGL': [396, 461, 475],
    'EPSY': [490, 590],
    'FIN': [490],
    'GLBL': [499],
    'INFO': [390, 490],
    'IS': [390, 490, 496, 497],
    'JOUR': [460, 480],
    'KIN': [494],
    'LING': [490],
    'MACS': [395, 496],
    'MCB': [493],
    'MSE': [498],
    'MUS': [404, 499],
    'NPRE': [498],
    'PHIL': [380],
    'PS': [300],
    'PSYC': [496],
    'SOC': [396, 496],
    'SOCW': [380],
    'TE': [398]
}

def get_req_needs(needs_row):
    # hours number + hourslabel, subreqs number + subreqslabel, count number, countlabel
    hours_needed = needs_row.find('span', class_='hours').text
    subreqs_needed = needs_row.find('td', class_='subreqs').text
    courses = needs_row.find('span', class_='count').text

    return {
        'hours': float(hours_needed or 0),
        'subreqs': int(subreqs_needed or 0),
        'courses': int(courses or 0)
    }

def get_subreq_needs(needs_row):
    hours_text = needs_row.find('td', class_='hours')
    hours_needed = hours_text.text if hours_text is not None else 0
    courses_text = needs_row.find('td', class_='count')
    courses = courses_text.text if courses_text is not None else 0
    # print(needs_row)
    courseslabel_text = needs_row.find('td', class_='countlabel')
    courseslabel = courseslabel_text.text.strip() if courseslabel_text is not None else ''
    if courseslabel == 'COURSES TAKEN' or courseslabel == 'COURSE TAKEN':
        courses = 0

    return {
        'hours': float(hours_needed),
        'courses': int(courses)
    }

def parse_course_select(from_list):
    courses = []
    elements = [child for td in from_list.find_all('td') for child in td.children]
    for i, element in enumerate(elements):
        if type(element) is Tag:
            prev_join_text = elements[i-1].strip() if i > 0 else ','
            next_join_text = elements[i+1].strip() if i < len(elements) - 1 else ','
            next_element = elements[i+2] if i < len(elements) - 2 else None
            department = element['department'].strip()
            course_number = element['number'].strip().split(' ')[0]
            for special_topic in SPECIAL_TOPICS.get(department, []):
                if course_number.startswith(str(special_topic)):
                    # Add section in for special topics
                    course_number = element.find('span', class_='number').text.replace('(X)', '').replace(department, '').strip()
                    break
            next_course_number = None if next_element is None else next_element['number'].strip()

            # Handle wildcard Courses, e.g. take any course in this department
            if course_number == '****':
                courses.append([{
                    'number': None,
                    'department': department
                }])
                continue
            # Handle level courses, e.g. take any 300 level course in this department
            elif course_number.endswith('**'):
                department = None if department == '*****' else department
                courses.append([{
                    'number': course_number,
                    'department': department
                }])
                continue


            if i == len(elements) - 1 or next_join_text in [',', '', '&']:
                if prev_join_text != 'OR':
                    courses.append([{
                        'number': course_number,
                        'department': department
                    }])
            elif next_join_text == 'OR':
                courses.append([{
                    'number': course_number,
                    'department': department,
                },{
                    'number': next_course_number,
                    'department': next_element['department'].strip(),
                }])
            elif next_join_text == 'TO':
                for course_number in range(int(course_number), int(next_course_number)):
                    courses.append([{
                        'number': str(course_number),
                        'department': department
                    }])
            else:
                raise ValueError('Invalid course join text: {}'.format(next_join_text))
    return courses

def parse_audit(html):
    audit = BeautifulSoup(html, 'html.parser')
    reqs_parsed = []
    reqs = audit.find_all('div', class_='requirement')
    courses_taken_section = None
    for req in reqs:
        req_name = req.find('div', class_='reqTitle').get_text("\n").strip()
        req_OK = 'Status_OK' in req["class"] or 'Status_NONE' in req["class"]
        if 'summary of courses taken' in req_name.lower():
            courses_taken_section = req
            continue
        if not req_OK and 'Status_NO' not in req["class"]:
            continue
        

        req_needs = {
            'hours': 0,
            'courses': 0,
            'subreqs': 0
        }
        subreqs_parsed = []
        if not req_OK:
            req_table = req.find('tr', class_='reqNeeds')

            # Parse subreqs
            subreqs = req.find_all('div', class_='subrequirement')
            prev_subreq_number = 0
            for subreq in subreqs:
                # print(subreq)
                title = subreq.find('span', class_='subreqTitle')
                status_icon = subreq.find('span', class_='status')['class']
                status_icon_none =  'Status_NONE' in status_icon
                status_icon_ok = 'Status_OK' in status_icon
                subreq_number = subreq.find('span', class_='subreqNumber').text.replace(')', '').strip()
                if subreq_number == 'OR':
                    subreq_number = prev_subreq_number
                elif subreq_number == '':
                    subreq_number = len(subreqs_parsed) + 1
                else:
                    subreq_number = int(subreq_number)
                if title is None:
                    # print(f'Warning: NO TITLE, using parent title ({req_name})')
                    subreq_name = f'{req_name}'
                else:
                    subreq_name = title.get_text("\n").strip()
                    if len(subreq_name) == 0:
                        # print(f'Warning: EMPTY TITLE, using parent title ({req_name})')
                        subreq_name = f'{req_name}'
                subreq_OK = False
                if status_icon_ok:
                    subreq_OK = True
                elif title is None and req_OK:
                    subreq_OK = True
                elif title is not None and ('srTitle_substatusOK' in title["class"] or 'srTitle_substatusIP' in title["class"]):
                    subreq_OK = True
                # print(subreq_name, subreq_OK, title)
                # print(status_none)
                if title is not None and not subreq_OK and 'srTitle_substatusNO' not in title["class"]:
                    # print("Skipping subreq: {}".format(subreq_name))
                    continue

                if courses_taken_section is None and 'courses counting toward' in subreq_name.lower():
                    courses_taken_section = subreq

                from_list = None
                from_list = subreq.find('table', 'selectcourses')
                if from_list:
                    from_list = from_list.find('td', class_='fromcourselist')
                courses = []
                if not subreq_OK and from_list:
                    courses = parse_course_select(from_list)

                # Parse general education subreqs by marking course_list as a string of the req code
                # See https://github.com/wadefagen/datasets/tree/master/geneds#data-format
                gened_lookup_table = {
                    'advanced composition': 'ACP_',
                    'cultural studies': 'CS',
                    'humanities & the arts': 'HUM',
                    'natural sciences & technology': 'NAT',
                    'quantitative reasoning': 'QR',
                    'social & behavioral science': 'SBS',
                    'liberal education': 'LE',
                }
                for key in gened_lookup_table:
                    if key in subreq_name.lower() or key.replace('&', 'and') in subreq_name.lower():
                        assert len(courses) == 0
                        courses = [[{
                            'department': 'GENED',
                            'number': gened_lookup_table[key]
                        }]]
                        break
                subreq_needs = None
                table = subreq.find('table', class_='subreqNeeds')
                if table is None:
                    subreq_needs = {
                        'hours': 0,
                        'courses': len(courses)
                    }
                else:
                    subreq_needs = get_subreq_needs(table)
                subreq_needs['course_list'] = courses

                is_none = subreq_needs['hours'] == 0 and subreq_needs['courses'] == 0 and status_icon_none
                subreqs_parsed.append({
                    'name': subreq_name,
                    'subreq_number': subreq_number,
                    'OK': subreq_OK or is_none,
                    'needs': subreq_needs
                })
                prev_subreq_number = subreq_number
            
            if req_table is None:
                req_needs = {
                    'hours': 0,
                    'subreqs': len(list(filter(lambda x: x['OK'] == False, subreqs_parsed))),
                    'courses': 0
                }
            else:
                req_needs = get_req_needs(req_table)
        
        if len(subreqs_parsed) == 0:
            subreqs_parsed.append({
                'name': "Unknown",
                'subreq_number': 1,
                'OK': req_OK if req_needs['hours'] == 0 and req_needs['courses'] == 0 else False,
                'needs': {
                    'hours': req_needs['hours'],
                    'courses': req_needs['courses'],
                    'course_list': []
                }
            })
        
        reqs_parsed.append({
            'name': req_name,
            'req_number': len(reqs_parsed) + 1,
            'OK': req_OK,
            'needs': req_needs,
            'subreqs': subreqs_parsed
        })
    
    # Parse classes taken
    courses_taken = []
    assert courses_taken_section is not None
    courses = courses_taken_section.find_all('tr', class_='takenCourse')
    for course in courses:
        raw_term = course.find('td', class_='term').text.strip()
        term, year = raw_term[:2], int(raw_term[2:])
        raw_name = course.find('td', class_='course').text.strip()
        grade = course.find('td', class_='grade').text.strip()
        condition_code = course.find('td', class_='ccode').text.strip()
        # parse out name
        if condition_code == '>D': # Duplicated Course, ignore
            continue
        
        match = re.match(r'([A-Z]{2,5})\s+([\d-]{3})(\s+[A-Z1-9]{1,3})?', raw_name)
        if match:
            department = match.group(1)
            number = match.group(2)
            section = match.group(3).strip() if match.groups == 3 else ''
            if number.endswith('--'):
                number = number[:-2] + '**'
            for topic in SPECIAL_TOPICS.get(department, []):
                if number == topic:
                    number = f'{number} {section}'
            courses_taken.append({
                # We count summer classes as spring classes
                'term': 'Spring' if term == 'SP' or term == 'SU' else 'Fall',
                'year': 2000 + year - (1 if term == 'WI' else 0),
                'department': department,
                'number': number,
                'is_transfer': grade == 'TR',

            })

    # Add semester int to courses taken
    first_year, first_term = get_first_term({'courses_taken': courses_taken})
    semester_offset = 1 if first_term == 'Spring' else 0

    for course in courses_taken:
        # Mark courses transferred into university before you took uni classes as 0
        if course['is_transfer'] and course['year'] < first_year or \
            (course['year'] == first_year and course['term'] == 'Fall' and first_term == 'Spring'):
            course['semester'] = 0
            continue

        course['semester'] = (course['year'] - first_year) * 2 + semester_offset + (0 if course['term'] == 'Spring' else 1)
    
    # Parse student ID
    student_id = audit.find('table', class_='auditHeaderTable').findAll('td')[3].text.strip()
    return {
        'requirements': reqs_parsed,
        'student_id': student_id,
        'courses_taken': courses_taken
    }

def get_first_term(audit_result):
    first_term = None
    first_year = 9999
    for course in audit_result['courses_taken']:
        if (course['year'] < first_year or (course['year'] == first_year and course['term'] == 'Fall')) and not course['is_transfer']:
            first_term = course['term']
            first_year = course['year']
    return first_year, first_term
def get_remaining_requirements(audit_result):
    remaining = []
    for req in audit_result['requirements']:
        if not req['OK']:
            new_subreqs = []
            for subreq in req['subreqs']:
                if not subreq['OK']:
                    new_subreqs.append(subreq)
            remaining.append({
                **req,
                'subreqs': new_subreqs
            })
    return remaining