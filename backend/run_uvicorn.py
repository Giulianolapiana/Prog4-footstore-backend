import os
import uvicorn

BASE_DIR = os.path.dirname(__file__)
# Asegurarse de trabajar desde el directorio del backend
os.chdir(BASE_DIR)

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True, log_level='info')
