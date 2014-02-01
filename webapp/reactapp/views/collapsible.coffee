IssueReader = require '../issuereader.coffee'

{a, div, h5} = React.DOM


Collapsible = React.createClass
  render: -> 
    (div {className: 'panel panel-default'}, [
      (div {className: 'panel-heading'},
        h5 {className: 'panel-title'},
          a {
            className: 'data-bypass'
            'data-toggle': 'collapse'
            'data-parent': '#accordion'
            href: "/##{@props.unique}"
          }, @props.header)
      (div {
        id: "#{@props.unique}"
        className: "panel-collapse #{if @props.collapsed then 'collapse' else 'in'}"
        },
        (div {
          className: 'panel-body'
        }, @props.children)
      )
    ])


module.exports = Collapsible
