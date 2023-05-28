from create_pickle import create_pickle
import uuid
import pickle
import os
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


# Load the projects data from a pickle file
def initialize_data():
  #check if pickle exist and loads the data
  if os.path.isfile('projects.pickle'):
    with open('projects.pickle', 'rb') as f:
      projects_data = pickle.load(f)
    return projects_data
  else: #if not exist
    create_pickle() #create it and loads the data
    with open('projects.pickle', 'rb') as f:
      projects_data = pickle.load(f)
    return projects_data

projects = initialize_data() #set the projects data

# Handles saving the new project data to the pickle
def save_data(data):
  with open('projects.pickle', 'wb') as f:
    pickle.dump(data, f)


@app.route("/")
def home():
  return render_template("index.html.j2", name="Zsolt")

@app.route("/projects")
def get_projects():
  try:
    request_data = request.get_json() #checks for JSON in request
    if 'fields' in request_data:
      fields = request_data['fields']
      filtered_projects = filter_list_of_dicts(projects['projects'], fields)
      return jsonify(filtered_projects), 200
  except:
    pass  # if no JSON in the request, returns unfilterd data
  return jsonify(projects), 200



@app.route("/project", methods=['POST'])
def create_project():
  request_data = request.get_json()
  # Assign unique id for each item
  new_project_id = uuid.uuid4().hex[:24]
  new_task_id = uuid.uuid4().hex[:24]
  new_checklist_id = uuid.uuid4().hex[:24]
  
  # Dictionary in dictionary new_project[task[checklist]]
  new_project = {
    'name': request_data['name'],
    'creation_date': request_data['creation_date'],
    'project_id': new_project_id,
    'completed': request_data['completed'],
    'tasks': [{
      'name': request_data['name'],
      'task_id': new_task_id,
      'completed': request_data['completed'],
      'checklist':[{
        'name': request_data['name'],
        'completed': request_data['completed'],
        'checklist_id': new_checklist_id
      }]
      }],
    }

  projects['projects'].append(new_project)
  save_data(projects)
  return jsonify({'message': f'project created with id: {new_project_id}'}), 201


# Modified get_project function
@app.route("/project/<string:project_id>")
def get_project(project_id):
  for project in projects["projects"]:
    if project['project_id'] == project_id:
      return jsonify(project)
  return jsonify({'message': 'project not found'}), 404

# Set project status to complete
@app.route("/project/<string:project_id>/complete", methods=['POST'])
def complete_project(project_id):
  for project in projects["projects"]:
    if project['project_id'] == project_id:
      if project['completed']:
        return '', 200
      else:
        project['completed'] = True
        save_data(projects)
        return jsonify(project), 200
  return jsonify({'message': 'project not found'}), 404


@app.route("/project/<string:name>/tasks")
def get_project_tasks(name):
  for project in projects:
    if project['name'] == name:
      return jsonify({'tasks': project['tasks']})
  return jsonify({'message': 'project not found'}), 404


@app.route('/project/<string:project_id>/task', methods=['GET'])
def get_all_tasks_in_project(project_id):
  for project in projects['projects']:
    if project['project_id'] == project_id:
      try:
        request_data = request.get_json() #checks for JSON in request
        if 'fields' in request_data:
          fields = request_data['fields']
          filtered_tasks = filter_list_of_dicts(project['tasks'], fields)
          return jsonify({'tasks':filtered_tasks}), 200
      except:
        pass  # if no JSON in the request, returns unfilterd data
      return jsonify({'tasks':project['tasks']}), 200
  return jsonify({'message': 'Project not found'}), 404


@app.route("/project/<string:project_id>/task", methods=['POST'])
def add_task_to_project(project_id):
  request_data = request.get_json()
  for project in projects["projects"]:
    if project['project_id'] == project_id:
      new_task_id = uuid.uuid4().hex[:24]
      new_task = {
        'name': request_data['name'],
        'task_id': new_task_id,
        'completed': request_data['completed'],
        'checklist': []
      }
      if 'checklist' in request_data:
        for checklist_item in request_data['checklist']:
          new_checklist_id = uuid.uuid4().hex[:24]
          new_checklist_item = {
            'name': checklist_item['name'],
            'completed': checklist_item['completed'],
            'checklist_id': new_checklist_id
          }
          new_task['checklist'].append(new_checklist_item)
      project['tasks'].append(new_task)
      save_data(projects)
      return jsonify({'message': f'task created with id: {new_task_id}'}), 201
  return jsonify({'message': 'project not found'}), 404


# Create the filtered_dicts
def filter_list_of_dicts(list_of_dicts, fields):
    filtered_dicts = []
    for original_dict in list_of_dicts:
        dict_copy = original_dict.copy()
        for key in original_dict.keys():
            if key not in fields:
                del dict_copy[key]
        filtered_dicts.append(dict_copy)
    return filtered_dicts
