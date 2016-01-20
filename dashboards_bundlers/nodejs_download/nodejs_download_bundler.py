# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os
import io
import zipfile
from ipython_genutils.py3compat import cast_bytes

MAKEFILE_TMPL = '''\
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

.PHONY: run

run:
\tgit clone https://github.com/jupyter-incubator/dashboards_nodejs_app.git ; \
mv {notebook_filename} dashboards_nodejs_app/data/ ; \
cd dashboards_nodejs_app ; \
make build ; \
make run
'''

README_TMPL = '''\
This bundle includes foundation needed to get the included notebook running
as a NodeJS backend reference implementation for deployed dashboards within
a Docker container. To use it:

1. Run `make run` to build and run the dashboard-proxy with the included notebook.

Visit `http://<external docker IP>:9700/notebooks/{notebook_name}` to access the included notebook as a dashboard.
'''

def bundle(handler, abs_nb_path):
    '''
    Creates a zip file containing the original notebook, a Makefile, and a
    README explaining how to build the bundle. Does not automagically determine
    what base image, kernels, or libraries the notebook needs (yet?). Has the 
    handler respond with the zip file.
    '''
    # Notebook basename with and without the extension
    notebook_filename = os.path.basename(abs_nb_path)
    notebook_name = os.path.splitext(notebook_filename)[0]

    # Headers
    zip_filename = os.path.splitext(notebook_name)[0] + '.zip'
    handler.set_header('Content-Disposition',
                       'attachment; filename="%s"' % zip_filename)
    handler.set_header('Content-Type', 'application/zip')

    # Prepare the zip file
    zip_buffer = io.BytesIO()
    zipf = zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED)
    zipf.write(abs_nb_path, notebook_filename)
    zipf.writestr('Makefile', MAKEFILE_TMPL.format(**locals()))
    zipf.writestr('README.md', README_TMPL.format(**locals()))
    zipf.close()

    # Return the buffer value as the response
    handler.finish(zip_buffer.getvalue())