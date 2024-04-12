import os
from fastapi.testclient import TestClient
from bson import ObjectId
from pymongo import MongoClient
import pytest
from main import app

client = TestClient(app)
dbClient = MongoClient(os.getenv("MONGO_CONN_URL"))
db = dbClient['pyDb']

def test_get_courses_no_params():
    response = client.get("/courses")
    assert response.status_code == 200
    
def test_get_courses_sort_by_alphabetical():
    response = client.get("/courses?sort_by=alphabetical")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x:x['name']) == courses
    
def test_get_courses_sort_by_date():
    response = client.get("/courses?sort_by=date")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x:x['date'], reverse=True) == courses
    
def test_get_courses_sort_by_rating():
    response = client.get("/courses?sort_by=rating")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key = lambda x : x['rating']['total'], reverse=True) == courses

def test_get_courses_by_domain():
    response = client.get("/courses?domain=mathematics")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    
def test_get_courses_filter_by_domain_and_sort_by_alphabetical():
    response = client.get("/courses?domain=mathematics&sort_by=alphabetical")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    assert sorted(courses, key=lambda x:x['name']) == courses
    
def test_get_courses_filter_by_domain_and_sort_by_date():
    response = client.get("/courses?domain=mathematics&sort_by=date")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    assert sorted(courses, key=lambda x:x['date'], reverse=True) == courses
    
def test_get_course_by_id_exists():
    response = client.get("/courses/6618921781a595f2ad70cf40")
    assert response.status_code == 200
    course = response.json()
    course_db = db.courses.find_one({'_id': ObjectId('6618921781a595f2ad70cf40')})
    name_db = course_db['name']
    name_response = course['name']
    assert name_db == name_response
    
def test_get_course_by_id_not_exists():
    response = client.get("/courses/6618921781a595f2ad70c200")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Course not found, check provided id.'}
    
def test_rate_chapter():
    course_id = '6618921781a595f2ad70cf40'
    chapter_id = 1
    rating = 1
    
    response = client.post(f"/courses/rate/{course_id}/{chapter_id}?rating={rating}")
    assert response.status_code == 200
    
    assert "name" in response.json()
    assert "rating" in response.json()
    assert "total" in response.json()['rating']
    assert "count" in response.json()['rating']
    
    assert response.json()['rating']['total'] > 0
    assert response.json()['rating']['count'] > 0
    
def test_rate_chapter_not_exists():
    response = client.post("/courses/6618921781a595f2ad70cf40/990/rate", json={'rating': 1})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    