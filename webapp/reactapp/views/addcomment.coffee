IssueReader = require '../issuereader.coffee'

Collapsible = require './collapsible.coffee'
Media = require './media.coffee'

{
  a, 
  button, 
  div, 
  form, 
  h4, 
  img, 
  textarea
} = React.DOM


AddComment = React.createClass
  getInitialState: ->
    return {
      text: ''
    }

  handleSubmit: (e) ->
    e.preventDefault()
    
    # submit a new comment
    proxyCommentsUrl = @props.item.comments_url.replace 'https://api.github.com/', IssueReader.githubApiUrl
    $.ajax proxyCommentsUrl,
      type: 'post'
      dataType: 'json'
      contentType: 'application/json'
      data: JSON.stringify {
        body: @state.text
      }
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
          text: ''
        }

        @props.parent.setState {
          commentsData: @props.parent.state.commentsData.concat [data.data]
        }, => 
          @props.parent.openComments()



  onChange: (e) ->
    @setState {
      text: e.target.value
    }

  render: -> 
    (Collapsible {
      header: 'Add Comment'
      unique: "addcomment_#{@props.item.id}"
      collapsed: true
      }, (div {}, 
        form {onSubmit: @handleSubmit}, [
          textarea {
            className: 'col-xs-10', 
            rows: 3, 
            required: true
            onChange: @onChange
            value: @state.text
          }
          button {}, "Add a comment"
        ]
      )
    )

module.exports = AddComment
