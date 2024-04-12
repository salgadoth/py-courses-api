import os
import contextlib
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = MongoClient(os.getenv('MONGO_CONN_URL'))
db = client["pyDb"]

@app.get("/courses")
def get_courses(sort_by: str = 'date', domain: str = None):
    for course in db.courses.find():
        total = 0
        count = 0
        for chapter in course['chapters']:
            with contextlib.suppress(KeyError):
                total += chapter['rating']['total']
                count += chapter['rating']['count']
        db.courses.update_one({'_id': course['_id']}, {'$set': {'rating': {'total': total, 'count': count}}})
    
    if sort_by == 'date':
        sort_field = 'date'
        sort_order = -1
    elif sort_by == 'rating':
        sort_field = 'rating.total'
        sort_order = -1
    else:
        sort_field = 'name'
        sort_order = 1
        
    query = {}
    if domain:
        query['domain'] = domain
        
    courses = db.courses.find(query, {'name': 1, 'date': 1, 'description': 1, 'domain': 1, 'rating': 1, '_id': 0}).sort(sort_field, sort_order)

    return list(courses)

@app.get("/courses/{course_id}")
def get_course(course_id: str):
    print(course_id)
    course = db.courses.find_one({'_id': ObjectId(course_id)}, {'_id': 0, 'chapters': 0})
    if not course:
        raise HTTPException(status_code = 404, detail = 'Course not found, check provided id.')
    try:
        course['rating'] = course['rating']['total']
    except KeyError:
        course['rating'] = 'Not rated yet.'
        
    return course

@app.get("/courses/{course_id}/{chapter_id}")
def get_chapter(course_id: str, chapter_id: str):
    course = db.courses.find_one({'_id': ObjectId(course_id)}, {'_id': 0})
    
    if not course:
        raise HTTPException(status_code = 404, detail = 'Course not found, check provided id.')
    
    chapters = course.get('chapters', [])
    try:
        chapter = chapters[int(chapter_id)]
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code = 404, details='Chapter not found, check provided id.') from e

    return chapter

@app.post("/courses/rate/{course_id}/{chapter_id}")
def post_chapter_rating(course_id: str, chapter_id: str, rating: int = Query(..., gt=-2, lt=2)):
    course = db.courses.find_one({'_id': ObjectId(course_id)}, {'_id': 0})
    
    if not course:
        raise HTTPException(status_code=404, detail='Course not found')
    chapters = course.get('chapters', [])
    try:
        chapter = chapters[int(chapter_id)]
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=404, detail='Chapter not found') from e
    try:
        chapter['rating']['total'] += rating
        chapter['rating']['count'] += 1
    except KeyError:
        chapter['rating'] = {'total': rating, 'count': 1}
    db.courses.update_one({'_id': ObjectId(course_id)}, {'$set': {'chapters': chapters}})
    return chapter