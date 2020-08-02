# International mobility website - Astus International

## Add repository to VS Code

* Open a clean VS Code and type **Ctrl+Shift+P**
* Type "**git clone**" in the command window
* Type the following URL when prompted: **https://github.com/TCastus/Mobility-Website-Project**
* Select a location on your computer to store the contents of the GitHub repository
* When prompted, open the repository that has been created

**All the files and folders contained in the GitHub repository should have been downloaded**

## Push changes to the repository

* Save your changes
* Type **Ctrl+Shift+G**
* Type a message describing the changes you've made
* Type **Ctrl+Enter**
* Click the bottom-left **Synchronize Changes** icon
* Click **Ok** if a prompt appears

The changes should be saved to the repository and you should be able to see them online

## How to run this website

* Clone this repository if you haven't already done so
* Install (if not already done) the following: Python 3, MySQL, VS Code (for practicality)
* Create a virtual environment to work in
   * Install the virtualenv module: **python -m pip install virtualenv**
      * If already installed, use the following command: **python -m pip install virtualenv --upgrade**
   * Run the following command: **python -m venv MobilityWebsiteEnv**
   * Check the existence of a folder named **MobilityWebsiteEnv** containing two subfolder; **Lib** and **Scripts**. 
      * If this is not the case, you will most likely have encountered an error that should be displayed in the terminal window
* Activate the virtual environment (You should be located in the git repository folder)
   * Windows: **.\MobilityWebsiteEnv\Scripts\activate**
   * Linux/MacOS: **source MobilityWebsiteEnv/bin/activate**
   * You can confirm that you are in the virtual environment by typing **which python**. This should point to the MobilityWebsiteEnv directory
* Run the following command: **python -m pip install -r requirements.txt**
* Open **MySQL Workbench** and create a root user with/without a password
* Open **Local instance MySQL80** with the root user (The instance can also be named **Local instance MySQL Router**)
* Create a new schema with the name you like (The name used in this code is: **international_mobility_project**)
* Set it as the default schema
* Edit the settings files in the folder **internationalmobility/settings** with your specific database information
* Open a command prompt/terminal window in the folder containing **manage.py** and type: 
    * **python manage.py makemigrations**
    * **python manage.py migrate**
    * **python manage.py runserver**
* Open any browser and type: **localhost:8000/exchange/home**
* Congratulations, the website is up and running! Feel free to play around.

## Update database from django shell

* Open a terminal in the folder that contains **manage.py**
* Run the following command:
	* **python manage.py shell**
* Once in the shell, type **from exchange.models import \***
* You can now access and modify any element within the database

**Examples**

* Adding a new entry to a specific table:
	* Adding a new County: **newCountry = Country(CountryName="A Country", ECTSConversion=1, Countinent="AS")**
	* **newCountry.save()**
	* Note that you need to fill in all the fields that are required when creating a new entry (in the models.py file, any attribute that has a default value isn't required to be entered)

* Updating an existing entry:
	* **updatedEntry = Country.objects.get(ID=123)** (You need to know what entry you want to modify, you can find this out however you want using the ID, some of its attributes or any other method)
	* **updatedEntry.ECTSConversion=1.5**
	* **updatedEntry.save()**