IssueReader = require '../issuereader.coffee'

AddComment = require './addcomment.coffee'
Collapsible = require './collapsible.coffee'
Comments = require './comments.coffee'
Media = require './media.coffee'

{a, button, div, h4, hr, img, p} = React.DOM


IssueItem = React.createClass
  render: -> 
    theTime = moment.utc(@props.item.created_at).local() #.subtract('hours', 8)
    (div {}, [
      (Media {
        imageUrl: @props.item.user.html_url
        imageSrc: @props.item.user.avatar_url
        subtitle: @props.item.user.login
      }, (Collapsible {
          header: @props.item.title
          unique: "issue_#{@props.item.id}"
          collapsed: false
        }, (div {}, [
          p {}, [
            "URL: ",
            (a {
              href: @props.item.url
            }, @props.item.url),
            "   ------   Posted at: #{theTime.format('MM-DD-YYYY, h:mm:ss a ZZ')}"
          ]
          p {}, [
            "State: ",
            button {
              className: "#{if @props.item.state is 'open' then 'btn-success' else ''} #{if @props.item.state is 'closed' then 'btn-warning' else ''}"
            }, @props.item.state
          ]
          hr {}
          (div {
            dangerouslySetInnerHTML: {
              __html: IssueReader.converter.makeHtml(
                @props.item.body)
            }})
        ])
        )
      ),
      (Comments {
        item: @props.item
      }),
      (hr {})
    ])


module.exports = IssueItem
