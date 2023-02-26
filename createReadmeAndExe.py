import os
import json
from markdown import markdown
from pyhtml2pdf import converter

readmeFilename = 'README'
cwd = os.getcwd()
style = \
    """
    <style>
        table {
            "font-family: helvetica, sans-serif;"
            font-size: small;
            border-collapse: collapse;
        }

        td, th {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }

        tr:nth-child(even) {
            background-color: #dddddd;
        }

        *{
            font-family: helvetica, sans-serif;
        }

        code {
            font-family: "Courier New";
        }
    </style>
    """

def create_readme_pdf():
    with open(f'{readmeFilename}.md', 'r') as f:
        html_text = markdown(f.read(), output_format='html4')

    cwd = os.getcwd()
    html_text = html_text.replace('src="','src="' + cwd)
    html_text = style + html_text

    with open(f'{readmeFilename}.html', 'w') as f:
        f.write(html_text)

    path = os.path.abspath(f'{readmeFilename}.html')
    converter.convert(f'file:///{path}', f'{readmeFilename}.pdf')
    os.remove(f'{readmeFilename}.html')

def create_exe():
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

def copy_assets_to_output():
    if not os.path.exists(f"{cwd}/output"):
        os.mkdir(f"{cwd}/output")

    if not os.path.exists(f"{cwd}/output/Icons"):
        os.mkdir(f"{cwd}/output/Icons")

    os.popen(f'copy {cwd}\\{readmeFilename}.pdf {cwd}\\output\\{readmeFilename}.pdf')

    icons = os.listdir(f"{cwd}/Icons")
    for i in icons:
        os.popen(f'copy {cwd}\\Icons\\{i} {cwd}\\output\\Icons\\{i}')

create_readme_pdf()
copy_assets_to_output()
create_exe()