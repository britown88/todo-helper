import random
import time

from jinja2 import Template
from pygithub3 import Github

from db.todoRepos import Todo

titleTemplate = 'Unresolved TODO in {{ FileName }}:{{ LineNumber }}'
issueHeaderTemplate = 'File: {{ FilePath }}\nLine: {{ LineNumber }}\n\n\'\'\'\n{{ CommentBlock }}\n\'\'\''

#Builds a template and renders it with the passed-in data
def renderTemplate(tempString, data):
    return Template.render(Template(tempString), data)


#Returns a list of complain templates
def buildComplaintTemplatesList():
    templates = []
    
    templates.append('This has been sitting here since {{ BlameDate }}...a little unprofessional don\'t you think?')
    templates.append('I don\'t get it, {{ BlameFirstName }} added this {{ BlameDatePhrase }} ago!')
    templates.append('Why was @{{ BlameUsername }} allowed to leave this here?')
    templates.append('We\'ve had no traction on this since {{ BlameDate}}.')
    templates.append('I thought {{ FileName }} was in @{{ BlameUserName }}\'s hands?')
    templates.append('It\'s been {{ BlameDatePhrase }}.')
    
    return templates
    
#Returns a list of emphasis templates
def buildEmphasisTemplatesList():
    templates = []
    
    templates.append('Seriously.')
    templates.append('Is there ever going to be any progress on this?')
    templates.append('I\'m confused as to why this is still a TODO...')
    templates.append('Couldn\'t you just go ahead and implement this?')
    templates.append('I find it pretty hilarious that this continues to go unresolved.')
    templates.append('Will we be seeing resolution on this in this project\'s lifetime?')
    templates.append('I think I speak for many when I say that the lack of update on this is non-trivially detrimental.')
    templates.append('How can we expect to have full-featured release when the code itself is fragmented and incomplete?')
    
    return templates

#Builds and returns the dictionary to popuate templates with
#Takes a db.todoRepo.Todo()
def buildTemplateData(todo):
    data = {}
    
    userFormalName = buildUserFormalName(todo.blameUser)
    
    data['BlameUserName'] = todo.blameUser
    data['BlameFirstName'] = userFormalName.split(' ')[0]
    data['BlameDate'] = todo.blameDate
    data['BlameDatePhrase'] = buildDatePhrase(todo.blameDate)
    data['FileName'] = todo.filePath.rsplit('/', 1)[1].split('.')[0]
    data['FilePath'] = todo.filePath
    data['LineNumber'] = todo.lineNumber
    data['CommentBlock'] = todo.commentBlock
    
    return data

#Grabs data on the entered username from Github and returns the user's full name
#Returns an empty string if the user is not found
def buildUserFormalName(username):
    gh=Github()
    user = None
    
    try:
        user = gh.users.get(username)
    except:
        #User wasnt found for some reason
        pass
    
    return user.name if user else ''
    
#Builds a string describing the passed date relative to the current date 
#in a human-readable phrase
#Passed in data shoud be in 'yyyy-mm-dd' and be GMT
def buildDatePhrase(dateString):
    date = time.strptime(dateString, '%Y-%m-%d')
    currDate = time.gmtime()
    
    elapsedSeconds = time.mktime(currDate) - time.mktime(date)
    elapsedHours = (elapsedSeconds / 60) / 60
    elapsedDays = elapsedHours / 24
    elapsedWeeks = elapsedDays / 7.019
    elapsedMonths = elapsedDays / 30.41
    elapsedYears = elapsedDays / 365
    
    if elapsedYears > 2:
        return 'over %i years' % (elapsedYears)
    
    if elapsedYears > 1:
        return 'over a year'
        
    if elapsedMonths > 10:
        return 'almost a year'
        
    if elapsedMonths > 2:
        return 'over %i months' % (elapsedMonths)
        
    if elapsedMonths > 1:
        return 'over a month'
        
    if elapsedWeeks > 3:
        return 'almost a month'
        
    if elapsedWeeks > 2:
        return 'over %i weeks' % (elapsedWeeks)
        
    if elapsedWeeks > 1:
        return 'over a week'        
        
    if elapsedDays > 5:
        return 'almost a week'
        
    if elapsedDays > 2:
        return '%i days' % (elapsedDays)
        
    if elapsedDays > 1:
        return 'a long day'        

    return 'crucial hours'
    
#Compiles the different parts of the issue's body and returns the final string
#Takes the data dictionary to render the templates with
def buildIssueBody(data):
    emphasisList = buildEmphasisTemplatesList()
    complaintList = buildComplaintTemplatesList()
    
    emphasisTemplate = emphasisList[random.randint(0, len(emphasisList) - 1)]
    complaintTemplate = complaintList[random.randint(0, len(complaintList) - 1)]
    
    header = renderTemplate(issueHeaderTemplate, data)
    emphasis = renderTemplate(emphasisTemplate, data)
    complaint = renderTemplate(complaintTemplate, data)
    
    return '%s\n\n%s  %s' % (header, complaint, emphasis)


#Builds an issue from the passed db.todoRepos.Todo
#returns a dictionary containing title and body ready to pass to github
def buildIssue(todo):
    #Create Issues format
    #repo.create(dict(title='My test issue', body='This needs to be fixed ASAP.'))
    
    #Build Title
    #Build First line containing filename and line#
    #Quote the todo comment block
    #Message (Build dict to send to templates), message consists of Complaint followed by Emphasis
    #Return {title, body}
    
    data = buildTemplateData(todo)
    ret = {}
    
    ret['title'] = renderTemplate(titleTemplate, data)
    ret['body'] = buildIssueBody(data)
    
    return ret
    


