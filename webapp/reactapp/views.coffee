###*
  @jsx React.DOM
###

IssueReader = require "./issuereader.coffee"


Media = require "./views/media.coffee"

Overview = require "./views/overview.coffee"


Views = {}

Views.Media = Media
Views.Overview = Overview

module.exports = Views
