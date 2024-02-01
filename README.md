# Window OCR Screenshot Tool 
As its name suggests, this project builds a Python application specifically for Windows that allows you to take screenshots and convert them to text (Optical Character Recognition), along with several text transformation options (translate using Google API, remove line breaks, etc.). The resulting text will be automatically added to your Windows clipboard. The application uses EasyOCR for converting text from images, supporting both English and Vietnamese. To add more languages, you can easily achieve this by modifying the options in the utils/image_processor.py file.

## Demo
![](/resources/demo.gif)



## Installation 
**Download Pre-built Application**: A pre-built version of the application is available for download. Please access the application through this [link](https://studenthcmusedu-my.sharepoint.com/:u:/g/personal/20280078_student_hcmus_edu_vn/Ea55fYvSSKZBgRnSVmo-DXIBmgWpRgjwI1n0j5k05a0Tsg?e=nk06Qz)

**Build From Source**: For those preferring to build the application from source, follow the steps below. 
1. Creating a Python virtual environment. If unfamiliar with this process, consult this [tutorial](https://www.google.com/search?sca_esv=606dd81dc728d262&sxsrf=ACQVn08HmkryY-H0n3rrGVX3vX9MsVYSCQ:1706710469879&q=install+python+and+create+virtual+environment+on+windows&spell=1&sa=X&ved=2ahUKEwiavaX654eEAxVJa_UHHad0CIUQBSgAegQICBAC&biw=1536&bih=747&dpr=1.25)
2. Open command line on your window, activate your created virtual environment and run following commands
```sh
cd path/to/place/your/built/application
set projectPath=path/to/root/of/code/directery/ # note: path should not contain space
pip install -r %projectPath%requirements.txt
pip uninstall -y opencv-python 
pip uninstall -y opencv-python-headless 
pip install opencv-python==4.6.0.66
pip install pyinstaller==6.3.0
pyinstaller --noconfirm --onedir --windowed --icon "%projectPath%resources/app_icon.ico" --add-data "%projectPath%resources;resources/" --add-data "%projectPath%setup;setup/" --add-data "%projectPath%utils;utils/" --add-data "%projectPath%constants.py;."  "%projectPath%OCR-S.py"
```
> **Notes**
> - You may need to grant the application permission to run at Windows startup. Alternatively, you can manually open the application without utilizing this feature.
> - The translation feature may occasionally fail due to updates or changes in the googletrans package. If this occurs, updating the package to the latest version and rebuilding the app should resolve the issue.


## Future Improvements
- Replace ToastNotifier with an alternative method for more editable text result capabilities.
- Develop a complete independent clipboard or integrate with an existing one to enable Linux compatibility.
- Create an independent OCR module from EasyOCR for more configurable options and improved accuracy