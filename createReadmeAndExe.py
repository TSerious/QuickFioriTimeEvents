import os
import json
from markdown import markdown
from pyhtml2pdf import converter

def create_readme_pdf():
    cwd = os.getcwd()
    filename = 'README'

    with open(f'{filename}.md', 'r') as f:
        html_text = markdown(f.read(), output_format='html4')

    cwd = os.getcwd()
    html_text = html_text.replace('src="','src="' + cwd)

    with open(f'{filename}.html', 'w') as f:
        f.write(html_text)

    path = os.path.abspath(f'{filename}.html')
    converter.convert(f'file:///{path}', f'{filename}.pdf')
    os.remove(f'{filename}.html')

def create_exe():
    cwd = os.getcwd()
    f = open('auto-py-to-exe_config.json')
    data = json.load(f)
    f.close()
    options = data["pyinstallerOptions"]
    for i in options:
        if i["optionDest"] == "filenames":
            i["value"] = f"{cwd}/StartInTray.py"
        if i["optionDest"] == "icon_file":
            i["value"] = f"{cwd}/Icons/default.ico"
 
    with open("auto-py-to-exe_config.json", "w") as outfile:
        json.dump(data, outfile)

    os.system('auto-py-to-exe -c auto-py-to-exe_config.json')

create_readme_pdf()
create_exe()