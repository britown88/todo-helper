IssueReader = require '../issuereader.coffee'

IssueItem = require './issueitem.coffee'
Media = require './media.coffee'

{
  button,
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
    @getIssues(0)
    @getMeta()
    @getQueue()
    return {
      issueUrl: '/issues'
      issuesData: []
      issuesMeta: {}
      queue: {}
      nextPage: 0
      loading: true
    }

  getIssues: (pageNumber)->
    $.ajax "/issues/#{pageNumber}",
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

          newIssues = @state.issuesData.concat if _.has(data.data, 'length') then data.data else []

        @setState {
          issuesData: newIssues
          nextPage: @state.nextPage + 1
          loading: false
        }

  getMoar: ->
    @setState {
      loading: true
    }
    @getIssues @state.nextPage

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
        console.log data
        @setState {
          issuesMeta: data.data
        }

  getQueue: ->
    $.ajax "/redis-stats",
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
          queue: data.data
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
          (p {}, "RateLimit reset: #{moment(@state.issuesMeta.rate.reset, 'X').format('MMM Do YYYY, h:mm:ss a ZZ')}")
        ]) else '',
        if @state.queue then (div {className: 'meta-container pull-right'}, [
          (p {}, "Issues posted: #{@state.queue.postedIssueCount}"),
          (p {}, "Repos Touched: #{@state.queue.repoCount}"),
          (p {}, "Ready to clone: #{@state.queue.cloneCount}"),
          (p {}, "Ready to parse: #{@state.queue.parseCount}"),
          (p {}, "Ready to post: #{@state.queue.postCount}"),
        ]) else '',
      ),
      (hr {className: 'clear'}),
      (div {}, [
        @state.issuesData.map(@createItem)
      ]),
      (button {
        className: "btn #{if @state.loading then 'btn-disabled' else 'btn-info'}",
        disabled: @state.loading,
        onClick: @getMoar,
        }, "MOAR (or, a handful more.)")
      (hr {className: 'clear tall70'}),
    ])


module.exports = Overview





