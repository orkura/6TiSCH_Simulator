import os
import tempfile
import zipfile

import bottle as btl

import backend


def _get_result_path(result_name):
    if (
            isinstance(result_name, str) is False
            or result_name in ['', '.', '..']
            or os.path.basename(os.path.normpath(result_name)) != result_name
        ):
        btl.abort(400, 'Invalid result name')

    sim_data_path = os.path.abspath(backend.SIM_DATA_PATH)
    result_path = os.path.abspath(os.path.join(sim_data_path, result_name))
    if os.path.commonpath([sim_data_path, result_path]) != sim_data_path:
        btl.abort(400, 'Invalid result name')

    return result_path


@btl.get('/')
def get_index():
    return btl.static_file(
        'index.html',
        root=backend.get_web_root_path()
    )


@btl.get('/config.json')
def get_config_json():
    filename = os.path.basename(backend.SIM_CONFIG_PATH)
    root = os.path.dirname(backend.SIM_CONFIG_PATH)
    return btl.static_file(filename, root=root, download=filename)


@btl.get('/result/<result_zip_file_name:re:.*\\.zip>')
def get_result_zip_file(result_zip_file_name):
    result_subdir_name = result_zip_file_name[:-4]
    result_subdir_path = _get_result_path(result_subdir_name)
    if os.path.isdir(result_subdir_path):
        var_dir = backend.BACKEND_VAR_DIR_PATH
        fd, tmp_file_path = tempfile.mkstemp(
            suffix = '.zip',
            prefix = 'tmp',
            dir    = var_dir
        )
        os.close(fd)
        with zipfile.ZipFile(tmp_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(result_subdir_path):
                for file in files:
                    arcname = os.path.join(
                        os.path.relpath(root, result_subdir_path),
                        os.path.basename(file)
                    )
                    zipf.write(
                        filename = os.path.join(root, file),
                        arcname  = arcname
                    )
        ret = btl.static_file(
            os.path.basename(tmp_file_path),
            root     = var_dir,
            download = result_subdir_name + '.zip'
        )
        return ret
    else:
        btl.abort(404, 'Not Found')
