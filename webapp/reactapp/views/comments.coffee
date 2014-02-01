IssueReader = require '../issuereader.coffee'

AddComment = require './addcomment.coffee'
Collapsible = require './collapsible.coffee'
Media = require './media.coffee'

{a, div, h4, img} = React.DOM


Comments = React.createClass
  getInitialState: ->
    if @props.item.comments > 0
      @getComments()
    return {
      commentsData: []
    }

  getComments: ->
    proxyCommentsUrl = @props.item.comments_url.replace 'https://api.github.com/', IssueReader.githubApiUrl
    $.ajax proxyCommentsUrl,
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
          commentsData: data.data
        }

  openComments: ->
    # not right now, doesn't make sense.
    # $("#comments_#{@props.item.id}").collapse()

  createItem: (item) ->
    return Media {
      imageUrl: item.user.html_url
      imageSrc: item.user.avatar_url
      subtitle: item.user.login
    }, item.body

  render: -> 
    console.log @state
    return (div {className: "comments-container"}, [
      if @state.commentsData.length > 0 then (Collapsible {
        header: "Comments (#{@state.commentsData.length})"
        unique: "comments_#{@props.item.id}"
        collapsed: false
        }, [
        @state.commentsData.map(@createItem)
      ]) else '',
      (AddComment {
        item: @props.item
        parent: @
      }),
    ])



module.exports = Comments
