from webdrivermanager import GeckoDriverManager

try:
    gdd = GeckoDriverManager()
    

    version = gdd.get_latest_version()
    print(f"Latest version is: {version}")

    path = gdd.download_and_install()

    print(f"Driver installed to: {path}")
except Exception as e:
    print(f"{str(e)}")

#input()