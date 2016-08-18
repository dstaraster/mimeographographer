from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, widgets, BooleanField
from wtforms.validators import DataRequired

class InstanceForm(Form):
    url = StringField('url', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class DomainForm(Form):
    domain = SelectField("domain", validators=[DataRequired()])

class ProjectForm(Form):
    project = SelectField("project", validators=[DataRequired()])

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput('T')

class TableListForm(Form):
    selectDeselect = BooleanField()
    tableList = MultiCheckboxField('tableList')