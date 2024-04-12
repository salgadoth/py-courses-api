import pymongo
import json

client = pymongo.MongoClient("mongodb+srv://db_consumer:L357UcuLGFnEba8v@cluster0.y5d0bmy.mongodb.net/pyDb?retryWrites=true&w=majority&appName=Cluster0")
db = client["pyDb"]
collection = db["courses"]

# Read courses from courses.json
with open("../courses.json", "r") as f:
    courses = json.load(f)

# Create index for efficient retrieval
collection.create_index("name")

# add rating field to each course
for course in courses:
    course['rating'] = {'total': 0, 'count': 0}
    
# add rating field to each chapter
for course in courses:
    for chapter in course['chapters']:
        chapter['rating'] = {'total': 0, 'count': 0}

# Add courses to collection
for course in courses:
    collection.insert_one(course)

# Close MongoDB connection
client.close()