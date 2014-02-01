
IssueReader =

  converter: new Showdown.converter()

  # githubApiUrl: 'https://api.github.com/'
  githubApiUrl: '/api/'

  now: ->
    moment()

  hitUtopias: (urlPath, data, options) ->
    url = IssueReader.buildUri urlPath, data
    $.ajax url,
      type: 'GET'
      contentType: ''
      dataType: 'json'
      contentType: 'text/json'
      timeout: 20000
      xhrFields:
        withCredentials: true
      error: (xhr, status, errorThrown) =>
        if options.error
          options.error()
        @addAlert
          context: 'error'
          message: new Handlebars.SafeString """
            AJAX Error: #{status}<br/>
            AJAX error thrown: #{errorThrown}<br />
            AJAX XHR: #{xhr}<br />
            """
      success: options.success

  clearAlerts: ->
    $('#alerts').empty()

  addAlert: (alert) ->
    if alerts.keepPreviousMessages
      # remove old alerts
      $('#alerts').empty()
    # add the new one
    $('#alerts').append(alert.message)

  # Keep active application instances namespaced under an app object.
  app: _.extend({}, Backbone.Events)

module.exports = IssueReader


