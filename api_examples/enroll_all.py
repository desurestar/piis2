import requests

username = 'your_username'
password = 'your_password'
base_url = 'http://127.0.0.1:8000/api/'
url = f'{base_url}courses/'
available_courses = []
all_courses = []

while url is not None:
    print(f'Loading courses from {url}')
    r = requests.get(url)
    response = r.json()
    url = response.get('next')
    courses = response.get('results', [])
    available_courses += [course['title'] for course in courses]
    all_courses.extend(courses)

print(f"Available courses: {','.join(available_courses)}")

for course in all_courses:
    course_id = course['id']
    course_title = course['title']
    r = requests.post(
        f'{base_url}courses/{course_id}/enroll/',
        auth=(username, password),
    )
    if r.status_code == 200:
        print(f'Successfully enrolled in {course_title}')
    else:
        print(f'Failed to enroll in {course_title}: {r.status_code} {r.text}')
