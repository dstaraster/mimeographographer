from flask import render_template, redirect, request
from app import app
from .forms import InstanceForm, DomainForm, ProjectForm, TableListForm
import httplib2
import json
import re

http = httplib2.Http()
global url
global sourceForm
global domainForm
global projectForm
global targetForm
global domain
global project
global tableList
global selectedTables
global targetDomain
global targetDomainForm
global targetProjectForm
global targetProject
global sourceInstance
global targetInstance

@app.route('/', methods=['GET', 'POST'])
def index():
    global sourceForm
    sourceForm = InstanceForm()
    if sourceForm.validate_on_submit():
        global url
        global sourceInstance
        sourceInstance = request.form['url']
        url = "http://localhost:8080/instances/" + sourceInstance
        # we're going to fudge authentication;
        # backend will always use perf creds
        # username = request.form['username']
        # password = request.form['password']
        return redirect('/sourceDomains')
    return render_template('index.html',
                           sourceForm=sourceForm)

@app.route('/sourceDomains', methods=['GET', 'POST'])
def sourceDomains():
    global url
    response, content = http.request(url + '/domains', 'GET')
    if response.status == 200:
        domains = json.loads(content.decode('utf-8'))
        global domainForm
        domainForm = DomainForm()
        add_domains(domainForm, domains)
        url = url + '/domains'
        return render_template('sourceDomains.html',
                               sourceForm=sourceForm,
                               domainForm=domainForm)
    global domain
    domain = request.form['domain']
    return redirect('/sourceProjects')

@app.route('/sourceProjects', methods=['GET', 'POST'])
def sourceProjects():
    global url
    global domain
    request_url = url + '/' + domain + '/projects'
    response, content = http.request(request_url, 'GET')
    if response.status == 200:
        projects = json.loads(content.decode('utf-8'))
        global projectForm
        projectForm = ProjectForm()
        add_projects(projectForm, projects)
        url = request_url
        return render_template('sourceProjects.html',
                               sourceForm=sourceForm,
                               domainForm=domainForm,
                               projectForm=projectForm)
    global project
    project = request.form['project']
    return redirect('/tableList')

@app.route('/tableList', methods=['GET', 'POST'])
def tableList():
    global url
    global project
    request_url = url + '/' + fixString(project) + '/lazyLoadFactTables'
    response, content = http.request(request_url, 'GET')
    if response.status == 200:
        global tableList
        tableList = json.loads(content.decode('utf-8'))
        tableListForm = TableListForm()
        add_tables(tableListForm, tableList)
        url = request_url
        return render_template('tableList.html',
                               sourceForm=sourceForm,
                               domainForm=domainForm,
                               projectForm=projectForm,
                                tableList=tableList['LazyLoadFactTableManifest'])
    global selectedTables
    selectedTables = request.values.getlist('tableList[]')
    return redirect('/targetInstance')

@app.route('/targetInstance', methods=['GET', 'POST'])
def targetInstance():
    global url
    global targetForm
    targetForm = InstanceForm()
    if targetForm.validate_on_submit():
        global url
        global targetInstance
        targetInstance = request.form['url']
        url = "http://localhost:8080/instances/" + targetInstance
        return redirect('/targetDomains')
    return render_template('targetInstance.html',
                           sourceForm=sourceForm,
                           domainForm=domainForm,
                           projectForm=projectForm,
                           tableList=tableList['LazyLoadFactTableManifest'],
                           targetForm=targetForm)

@app.route('/targetDomains', methods=['GET', 'POST'])
def targetDomains():
    global url
    request_url = url + '/domains'
    response, content = http.request(request_url , 'GET')
    if response.status == 200:
        domains = json.loads(content.decode('utf-8'))
        global targetDomainForm
        targetDomainForm = DomainForm()
        add_domains(targetDomainForm, domains)
        url = request_url
        return render_template('targetDomains.html',
                               sourceForm=sourceForm,
                               domainForm=domainForm,
                               projectForm=projectForm,
                               tableList=tableList['LazyLoadFactTableManifest'],
                               targetForm=targetForm,
                               targetDomainForm=targetDomainForm)
    global targetDomain
    targetDomain = request.form['domain']
    return redirect('/targetProjects')

@app.route('/targetProjects', methods=['GET', 'POST'])
def targetProjects():
    global url
    request_url = url + '/' + targetDomain + '/projects'
    response, content = http.request(request_url, 'GET')
    if response.status == 200:
        projects = json.loads(content.decode('utf-8'))
        global targetProjectForm
        targetProjectForm = ProjectForm()
        add_projects(targetProjectForm, projects)
        url = request_url
        return render_template('targetProjects.html',
                               sourceForm=sourceForm,
                               domainForm=domainForm,
                               projectForm=projectForm,
                               tableList=tableList['LazyLoadFactTableManifest'],
                               targetForm=targetForm,
                               targetDomainForm=targetDomainForm,
                               targetProjectForm=targetProjectForm)
    global targetProject
    targetProject = request.form['project']
    return redirect('/copyDatasets')

@app.route('/copyDatasets', methods=['GET', 'POST'])
def copyDatasets():
    request_url = "http://localhost:8080/instances/" + sourceInstance \
                    + '/domains/' + domain \
                    + '/projects/' + fixString(project) \
                    + '/lazyLoadFactTables/'
    destination = '/targetInstances/' + targetInstance + '/targetDomains/' + targetDomain + '/targetProjects/' + fixString(targetProject) + '/copy'
    copied = []
    for table in selectedTables:
        temp_url = request_url + fixString(table) + destination
        response, content = http.request(request_url + fixString(table) + destination)
        if response.status == 200:
            copied.append(table);
    return render_template('done.html',
                           sourceInstance=sourceInstance,
                           sourceDomain=domain,
                           sourceProject=project,
                           targetInstance=targetInstance,
                           targetDomain=targetDomain,
                           targetProject=targetProject,
                           copied=copied)


def add_domains(DomainForm, domains):
    DomainForm.domain.choices = [(d, d) for d in domains]

def add_projects(ProjectForm, projects):
    ProjectForm.project.choices = [(p, p) for p in projects]

def add_tables(TableListForm, tableList):
    TableListForm.tableList.choices = [(t, t) for t in tableList['LazyLoadFactTableManifest']]

def fixString(orig):
    #replace spaces with '+'
    return re.sub(r'\b \b', '+', orig)
