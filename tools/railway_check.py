import requests
import sys
import os
import json

# Railway GraphQL API Configuration
URL = "https://backboard.railway.com/graphql/v2"
TOKEN = "59c1fd97-4c54-4227-ae29-a4a155ec4131"
PROJECT_ID = "14ab2755-444a-4c8a-a822-01fa439b8519"

def run_query(query, variables=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    try:
        response = requests.post(URL, headers=headers, json={'query': query, 'variables': variables}, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def diagnostic_project():
    # Direct query for the project since we have its ID
    query = """
    query($id: String!) {
      project(id: $id) {
        name
        services {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
    """
    print(f"[RAILWAY] Querying project {PROJECT_ID}...")
    res = run_query(query, {"id": PROJECT_ID})
    
    if 'data' in res and res['data'] and res['data'].get('project'):
        project = res['data']['project']
        print(f"SUCCESS! Project: {project['name']}")
        services = project.get('services', {}).get('edges', [])
        for s_edge in services:
            service = s_edge['node']
            print(f"  - Service: '{service['name']}' (ID: {service['id']})")
    else:
        print(f"FAILED: {json.dumps(res, indent=2)}")

if __name__ == "__main__":
    diagnostic_project()
