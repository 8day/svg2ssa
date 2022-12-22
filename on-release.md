when making new release, in Notepad++:
1. run `cmd /c bandit -r "$(CURRENT_DIRECTORY)" & pause`.
2. run `cmd /c pylint "$(FULL_CURRENT_PATH)" --rcfile "$(CURRENT_DIRECTORY)\pyproject.toml" & pause`.
3. run `cmd /c black "$(CURRENT_DIRECTORY)" & pause`.
4. set version in `pyproject.toml` to `{YYYY}.{MM}.{DD}.{release-SID-for-the-day}`.
5. set version tag to `v{YYYY}.{MM}.{DD}.{release-SID-for-the-day}` for the latest commit from which the release will be made.
6. run `poetry lock`.
7. run `poetry build`.
