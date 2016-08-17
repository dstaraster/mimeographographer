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
global domain
global project
global TableListForm

@app.route('/', methods=['GET', 'POST'])
def index():
    global sourceForm
    sourceForm = InstanceForm()
    if sourceForm.validate_on_submit():
        global url
        url = "http://localhost:8080/instances/" + request.form['url']
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
        tableList = json.loads(content.decode('utf-8'))
        global tableListForm
        tableListForm = TableListForm()
        add_tables(tableListForm, tableList)
        url = request_url
        return render_template('tableList.html',
                               sourceForm=sourceForm,
                               domainForm=domainForm,
                               projectForm=projectForm,
                               tableListForm=tableListForm)
    return redirect('/sourceProjects')

def add_domains(DomainForm, domains):
    DomainForm.domain.choices = [(d, d) for d in domains]

def add_projects(ProjectForm, projects):
    ProjectForm.project.choices = [(p, p) for p in projects]

def add_tables(TableListForm, tableList):
    TableListForm.tableList.choices = [(t, t) for t in tableList['LazyLoadFactTableManifest']]

def fixString(orig):
    #replace spaces with '+'
    return re.sub(r'\b \b', '+', orig)
