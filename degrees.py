import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])
                
    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    referencesChecked = list();

    #Using queue for breadth first search to find optimal solution    
    queueFrontier = QueueFrontier();

    sourceNeighbors = neighbors_for_person(source);
    if sourceNeighbors is None or len(sourceNeighbors) == 0:
        return None;

    # If the target has no neighbors then there would be no path to it. 
    targetNeighors = neighbors_for_person(target);
    if( targetNeighors is None or len(targetNeighors) == 0):
        return None;

    queue_neighbors(queueFrontier, sourceNeighbors, None);

    targetNode = find_shortest_path(target, referencesChecked, queueFrontier);
    if(targetNode is None):
        return None;

    #Get path by walking node heirarchy
    pathtotarget = list();

    pathtotarget.append(targetNode.state);

    while(targetNode.parent is not None) :
        pathtotarget.append(targetNode.parent.state);
        targetNode = targetNode.parent;

    pathtotarget.reverse();

    return pathtotarget;

def find_shortest_path(target, referencesChecked, queueFrontier):
    #get items from queue
    while(queueFrontier.empty() == False):
        #print ("Queue length = ", queueFrontier.len());

        currentNode = queueFrontier.remove();
        currentNeighbor = currentNode.state;

        #skip if we have referenced this person before
        try: 
            referencesChecked.index(currentNeighbor[1]);
        except:
            if( currentNeighbor[1] == target):
                #Found the connection, return the currentNode so we can trace the heirarchy to calculate the path.
                return currentNode;

            #Track which people we have visited/checked to avoid cyclic dependencies    
            referencesChecked.append(currentNeighbor[1]);
                
            #queue all neighbors of current element
            queue_neighbors(queueFrontier, neighbors_for_person(currentNeighbor[1]), currentNode);
            continue;

    return None;
        
def queue_neighbors(queueFrontier, neighbors, parent):
    for neighbor in neighbors:
        newNode = Node(neighbor, parent, None);
        queueFrontier.add(newNode);

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
