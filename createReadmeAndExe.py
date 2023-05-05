import os
from markdown import markdown
from pyhtml2pdf import converter
import pyinstaller_versionfile
import shutil

version="1.9"
outputFolder = "QuickFioriTimeEvents"
readmeFilename = 'README'
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
    print(f"Creating {readmeFilename}.pdf ...")

    with open(f'{readmeFilename}.md', 'r') as f:
        html_text = markdown(f.read(), output_format='html4')

    html_text = html_text.replace('</h1>',f' - v{version}</h1>')
    html_text = html_text.replace('src="','src="' + cwd)
    html_text = style + html_text

    with open(f'{readmeFilename}.html', 'w') as f:
        f.write(html_text)

    path = os.path.abspath(f'{readmeFilename}.html')
    converter.convert(f'file:///{path}', f'{readmeFilename}.pdf')
    os.remove(f'{readmeFilename}.html')

    print("Done")

def create_exe():
    print(f"Creating exe ...")

    if os.path.exists(f'{cwd}\\{outputFolder}\\QuickFioriTimeEvents.exe'):
        os.remove(f'{cwd}\\{outputFolder}\\QuickFioriTimeEvents.exe')

    os.system(f'pyinstaller --noconfirm --onefile --windowed -i"{cwd}\\Icons\\default.ico" --name "QuickFioriTimeEvents" --version-file "{cwd}/versionfile.txt" --distpath "{cwd}\\{outputFolder}" "{cwd}/StartInTray.py"')
    #os.system('auto-py-to-exe -c auto-py-to-exe_config.json')

    print("Done")

def copy_assets_to_output():
    print("Copying assets ...")

    if not os.path.exists(f"{cwd}/{outputFolder}"):
        os.mkdir(f"{cwd}/{outputFolder}")

    if not os.path.exists(f"{cwd}/{outputFolder}/Icons"):
        os.mkdir(f"{cwd}/{outputFolder}/Icons")

    os.popen(f'copy {cwd}\\{readmeFilename}.pdf {cwd}\\{outputFolder}\\{readmeFilename}.pdf')

    icons = os.listdir(f"{cwd}/Icons")
    for i in icons:
        os.popen(f'copy {cwd}\\Icons\\{i} {cwd}\\{outputFolder}\\Icons\\{i}')

    print("Done")

def create_version_file():

    print("Creating version file ...")

    pyinstaller_versionfile.create_versionfile(
        output_file="versionfile.txt",
        version=version,
        file_description=f"QuickFioriTimeEvents {version}",
        internal_name="QuickFioriTimeEvents",
        original_filename="QuickFioriTimeEvents.exe",
        product_name="QuickFioriTimeEvents"
    )

    print("Done")

def create_zip():
    print("Creating zip ...")
    shutil.make_archive(f"{version}", 'zip', f"{cwd}\\{outputFolder}")
    print("Done")

cwd = os.getcwd()
create_readme_pdf()
copy_assets_to_output()
create_version_file()
create_exe()
create_zip()