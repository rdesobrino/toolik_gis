# opus_parsing.py
A script to cut down on the copy-pasting of OPUS processing for survey data. 
## Steps
Upload data to OPUS as normal (remember you can zip files together to upload at once).
### From Gmail 

 - Select all OPUS emails at once, click the three stacked dots in the menu bar, and select `Forward as attachment`. Email the attached to yourself.  
 - Open this new email, click print to PDF in the upper right, and save to the appropriate Z: drive location.
 - Download all attachments at once. 
 - Unzip the downloaded folder, and drag and drop into the `\eml`folder in your local copy of this repo.

### In File Explorer
 - Double-click `opus_parsing.py` to execute. If you haven't set up Python scripts to automatically run when opened, you can right-click the script, select Open With, and navigate to the `python.exe` on your machine. 



### or if you'd like to execute from the command line

```
python filepath\opus_parsing.py -i path_to_folder_of_emls -n name_of_output_spreadsheet -o path_to\output_spreadsheet.csv
```
all inputs are optional. the script will look for a `\eml` folder and create a spreadsheet based on today's date. The output will also be printed to the terminal (tab-delimited) so that it can be copy and pasted into an average sheet. 





###### 24/10/14 Rd