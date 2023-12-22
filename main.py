from fastapi import FastAPI, Query, HTTPException, Path
from pydantic import BaseModel
from typing import Optional
import json

# Because you can only do GET requests in the browser, you have to use test your code in your local host (i.e. http://127.0.0.1:8000/docs)

app = FastAPI()

class Person(BaseModel):
    # Make id not required, because we'll calculate id for the user when a post request is submitted (see add_person function)
    id: Optional[int] = None
    name: str
    age: int
    gender: str


with open('people.json', 'r') as f:
    people = json.load(f)

@app.get('/person/{p_id}', status_code=200)
def get_person(p_id: int):
    # Queries all the instances of the id in the people.json file, but assuming each id is unique, it's only going to return one json object
    person = [p for p in people if p["id"] == p_id]

    return person[0] if len(person) > 0 else {}

# Because we're querying, we don't need to pass into the 'get'
@app.get("/search", status_code=200)
def search(age: Optional[int] = Query(None, title="Age", description="The age to filter for"), name: Optional[str] = Query(None, title="Name", description="The name to filter for")):
    people1 = [p for p in people if p["age"] == age]

    if name is None:
        if age is None:
            return people
        else:
            return people1
    else:
        # don't want to do p["name"] == name, because we want to be lenient on the passing parameters, so it can also work out if it's a substring of p["name"]
        people2 = [p for p in people if name.lower() in p["name"].lower()]
        if age is None:
            return people2
        else:
            combined = [p for p in people if name.lower() in p["name"].lower() and p["age"] == age]
            return combined

@app.post('/addPerson', status_code=201)
def add_person(person: Person):
    p_id = max([p["id"] for p in people]) + 1
    new_person = {
        "id": p_id,
        "name" : person.name,
        "age":person.age,
        "gender":person.gender
    }

    people.append(new_person)
    
    write_to_json()
    
    return {"Success": "Post request has been achieved"}

@app.put('/changePerson', status_code=204)
def change_person(person: Person):
    new_person = {
        "id":person.id,
        "name": person.name,
        "age":person.age,
        "gender":person.gender
    }

    for person in people:
        if person["id"] == new_person["id"]:
            people.remove(person)
            people.append(new_person)
            write_to_json()
    # If above code block doesn't go through, because it wouldn't return, then we throw an exception
    return HTTPException(status_code=404, detail=f"Person with id {person.id} does not exist")

# Usually with delete requests, it's status code 204, which means return 'no content'
@app.delete('/deletePerson/{p_id}', status_code=200)
# Can use Path or Query interchangeably
def delete_person(p_id: int = Path(title="id", description="id of person to delete from database")):
    if p_id:
        person_delete = [p for p in people if p["id"] == p_id]
        if len(person_delete) > 0:
            people.remove(person_delete[0])
            write_to_json()
            print(person_delete[0])
            return person_delete[0]
        else:
            return HTTPException(status_code=404, detail=f"The id is not valid or not found")
    return HTTPException(status_code=404, detail=f"The id is not valid or not found in the database")



# Write to json after changes are done (post or put requests)
def write_to_json():
    with open("people.json", "w") as f:
        json.dump(people, f)
