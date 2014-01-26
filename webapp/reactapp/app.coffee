
IssueReader = require "./issuereader.coffee"
Views = require "./views.coffee"

Router = Backbone.Router.extend

  views: {}

  routes:
    '(/)': 'index'

  index: ->
    @views.test = new Views.Overview()
    React.renderComponent(@views.test, document.getElementById('main'))


  initialize: ->
    Backbone.history.start
      pushState: true
      root: '/'


# Start up our app
IssueReader.app.router = new Router()

# All navigation that is relative should be passed through the navigate
# method, to be processed by the router.  If the link has a data-bypass
# attribute, bypass the delegation completely.
$('body').on "click", "a:not([data-bypass], .chzn-default, .chzn-single)", (evt) ->
  href = $(this).attr("href")

  # Ensure the protocol is not part of URL, meaning its relative.
  if href
    evt.preventDefault()
    IssueReader.app.router.navigate href, {trigger: true}

