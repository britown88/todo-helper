
module.exports = (grunt) ->

  # Project configuration.
  grunt.initConfig
    watch:
      browserify:
        files: [
          "reactapp/**/*.coffee"
        ]
        tasks: "browserify"

    browserify:
      'build/app.js': ['reactapp/app.coffee']
      options:
        transform: ['coffeeify', 'reactify']
        debug: true



  grunt.loadNpmTasks 'grunt-contrib-coffee'
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-browserify'
  grunt.registerTask 'default', 'watch'
