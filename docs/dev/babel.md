# pyBabel notes

## Update translation files

1. Re-scan your source code for translatable strings and update the .pot and .po files.
   ```
   pybabel extract -F babel.cfg -o translations/messages.pot --ignore-dirs venv .
   pybabel update -i translations/messages.pot -d translations
   ```
2. Review and edit translations: Open `.po` files and search for new strings and the keyword `fuzzy`
3. Recompile translations
   ```
   pybabel compile -d translations
   ```
