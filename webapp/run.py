#!flask/bin/python
import os
from flaskapp import app, options

if __name__ == "__main__":
    # print os.path.join(app.root_path, 'dev.py')
    # print os.path.exists(os.path.join(app.root_path, 'dev.py'))
    print app.root_path
    port = int(os.environ.get('PORT', 5060))
    if options['dev']:
        app.run(host="127.0.0.1", port=port, debug=True)
    else:
        app.run(host="0.0.0.0", port=port, debug=True)
