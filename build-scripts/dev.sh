cd ..
source ./.venv/bin/activate
cd api

NEW_DEPS=false

while [ ! $# -eq 0 ]; do
    case "$1" in 
        --new-deps)
            NEW_DEPS=true
            ;;
    esac
    shift
done

if [ "$NEW_DEPS" = true ]; then
    pip-compile requirements.in
fi

pip install -r requirements.txt
cd ..
cd api/app
fastapi run main.py