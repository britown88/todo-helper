
{a, div, h4, h5, img, p} = React.DOM

IssueReader = require '../issuereader.coffee'


Media = React.createClass
  render: ->
    return (div {className: 'media'}, [
      (a {className: 'pull-left', href: @props.imageUrl},
        [
          (img {
            className: 'media-object', 
            src: @props.imageSrc
            width: '80px'
            height: '80px'
          }),
          (p {}, @props.subtitle),
        ]
      ),
      (div {className:'media-body'},
        @props.children
      )
    ])


module.exports = Media
