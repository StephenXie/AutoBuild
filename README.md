# Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
For use with openhands autobuilder, place get_verification_script.py and parser.py in the root of the containerized environment.
# Run

```bash
python3 get_verification_script.py --repo <repo> --commit <commit>
```
