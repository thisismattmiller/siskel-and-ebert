import json
import requests
from thefuzz import fuzz


def do_sparql_query(title):
    sparql = """
    SELECT ?item ?itemLabel ?director ?directorLabel ?date WHERE {
    SERVICE wikibase:mwapi {
        bd:serviceParam wikibase:api "EntitySearch" .
        bd:serviceParam wikibase:endpoint "www.wikidata.org" .
        bd:serviceParam mwapi:search "<REPLACE>" .
        bd:serviceParam mwapi:language "en" .
        ?item wikibase:apiOutputItem mwapi:item .
        ?num wikibase:apiOrdinal true .
    }
    # ?item (wdt:P279|wdt:P31) wd:Q11424 .
    ?item wdt:P577 ?date .
                            optional{
                                ?item wdt:P57 ?director
                                    }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } # Helps get the label in your language, if not, then default for all languages, then en language

                            
    } ORDER BY ASC(?num) LIMIT 100

    """.replace("<REPLACE>", title)
    # print("sparql: ", sparql, flush=True)
    headers = {
        'Accept': 'application/sparql-results+json',
        'User-Agent': 'Reconcile script'
    }
    params = {
        'query' : sparql
    }
    print(".")
    try:
        response = requests.get(
            SPARQL_ENDPOINT,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the SPARQL request: {e}",flush=True)


    return data


# Wikidata SPARQL endpoint
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# Load the JSON file
with open('all_data.json', 'r') as f:
    all_data = json.load(f)


for movie in all_data:
    # if 'At First Sight' not in movie['title']:
    #     continue

    
    if 'wikidata_qid' in movie:
        # print(f"Movie {movie['title']} already has a Wikidata QID: {movie['wikidata_qid']}", flush=True)
        continue
    else:
        print(movie, flush=True)
        continue

    # get all the X entitie types

    # print("data: ", data, flush=True)
    lookup = {}
    found = False

    data = do_sparql_query(movie['title'])
    
    if len(data['results']['bindings']) == 0:
        data = do_sparql_query(movie['title_llm'])
        if len(data['results']['bindings']) > 0:
            print(f"Using LLM title for {movie['title']}: {movie['title_llm']}", flush=True)


    if len(data['results']['bindings']) == 0:
        print(f"No results found for {movie['title']}", flush=True)
        continue

    for result in data['results']['bindings']:
        # if movie['year_pub'] in result['date']['value'] and 'directorLabel' in result:   
        if 'directorLabel' in result:    

            # print(result, flush=True)
            # print(result['directorLabel']['value'], '||||', movie['director'])
            # print(fuzz.ratio(result['directorLabel']['value'], movie['director']))


            if fuzz.ratio(result['directorLabel']['value'], movie['director']) >= 80:
                print(result['itemLabel']['value'], '==',movie['title'], '||||', result['directorLabel']['value'] , '==', movie['director'] )
                found = result['item']['value'].split("/")[-1]
                break

            if movie['director'] in result['directorLabel']['value']:
                print(result['itemLabel']['value'], '==',movie['title'], '||||', result['directorLabel']['value'] , '==', movie['director'] )
                found = result['item']['value'].split("/")[-1]
                break

        # qid = result['item']['value'].split("/")[-1]
        # label = result['itemLabel']['value']
        # lookup[qid] = {
        #     "label": label,
        #     "qid": qid,
        #     "matching_doc_types": [],
        # }

    if found != False:
        # print(f"Found Wikidata entity for {movie['title']}: {found}", flush=True)
        movie['wikidata_qid'] = found

    with open('all_data.json', 'w') as f:
        json.dump(all_data, f, indent=4)     