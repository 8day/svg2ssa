When making new release, in Notepad++:
1. run `cmd /c bandit -r "$(CURRENT_DIRECTORY)" & pause` from the root of package.
2. run `cmd /c pylint "$(CURRENT_DIRECTORY)" --rcfile "$(CURRENT_DIRECTORY)\..\pyproject.toml" & pause` from the root of package.
3. run `cmd /c black "$(CURRENT_DIRECTORY)" & pause` from the root of package.
4. set version in `pyproject.toml` to `{YYYY}.{MM}.{DD}.{release_SID_for_the_day}`.
5. set version tag to `v{YYYY}.{MM}.{DD}.{release_SID_for_the_day}` for the latest commit from which the release will be made.
6. run `poetry lock`.
7. run `poetry build`.
8. make executable with cx_Freeze for every supported XML parser.
9. upload to PyPI with `poetry publish`.
