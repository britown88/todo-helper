
{a, div, h4, hr, img} = React.DOM

IssueReader = require '../issuereader.coffee'

AddComment = require './addcomment.coffee'
Collapsible = require './collapsible.coffee'
Comments = require './comments.coffee'
Media = require './media.coffee'

IssueItem = React.createClass
  render: -> 
    (div {}, [
      (Media {
        imageUrl: @props.item.user.html_url
        imageSrc: @props.item.user.avatar_url
        subtitle: @props.item.user.login
        heading: @props.item.title
      }, (Collapsible {
          header: @props.item.title
          unique: "issue_#{@props.item.id}"
        }, (div {
            dangerouslySetInnerHTML: {
              __html: IssueReader.converter.makeHtml(
                @props.item.body)
            }}))),
      (Comments {
        item: @props.item
      }),
      (hr {})
    ])


module.exports = IssueItem
