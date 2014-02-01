
IssueReader = require '../issuereader.coffee'

IssueItem = require './issueitem.coffee'

Media = require './media.coffee'

{
  div, 
  h4, 
  hr,
  legend,
  li,
  p,
  ul
} = React.DOM

Overview = React.createClass
  getInitialState: ->
    # hit ajax stuff
    @getIssues()
    @getMeta()
    return {
      issueUrl: 'https://api.github.com/repos/p4r4digm/todo-helper/issues'
      issuesData: []
      issuesMeta: {}
    }

  getIssues: ->
    $.ajax "#{IssueReader.githubApiUrl}repos/p4r4digm/todo-helper/issues",
      type: 'get'
      dataType: 'json'
      contentType: 'text/json'
      error: (xhr, status, errorThrown) =>
        IssueReader.addAlert
          context: 'error'
          message: """
            AJAX Error: #{status}<br/>
            AJAX error thrown: #{errorThrown}<br />
            AJAX XHR: #{xhr}<br />
            """
      success: (data, status, xhr) =>
        for item in data.data
          item.body = @safeBrackets item.body
          item.title = @safeBrackets item.title

        @setState {
          issuesData: if _.has(data.data, 'length') then data.data[0..9] else []
        }

  getMeta: ->
    $.ajax "#{IssueReader.githubApiUrl}rate_limit",
      type: 'get'
      dataType: 'json'
      contentType: 'text/json'
      error: (xhr, status, errorThrown) =>
        IssueReader.addAlert
          context: 'error'
          message: """
            AJAX Error: #{status}<br/>
            AJAX error thrown: #{errorThrown}<br />
            AJAX XHR: #{xhr}<br />
            """
      success: (data, status, xhr) =>
        @setState {
          issuesMeta: data.data
        }

  safeBrackets: (string) ->
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')

  createItem: (item) ->
    return IssueItem {
      item: item
    }

  render: ->
    return @transferPropsTo (div {}, [
      (div {}, 
        (div {className: 'title-container meta-container '}, [
          (legend {className: 'title-legend'}, "Issues from #{@state.issueUrl}")
        ]),
        if @state.issuesMeta.rate then (div {className: 'meta-container pull-right'}, [
          (p {}, "RateLimit: #{@state.issuesMeta.rate.limit}"),
          (p {}, "Remaining: #{@state.issuesMeta.rate.remaining}"),
          (p {}, "RateLimit reset: #{moment(@state.issuesMeta.rate.reset, 'X').format('MMMM Do YYYY, h:mm:ss a')}")
        ]) else '',
      ),
      (hr {className: 'clear'}),
      div {}, [
        @state.issuesData.map(@createItem)
      ]
    ])


module.exports = Overview





