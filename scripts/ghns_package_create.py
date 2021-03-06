##############################################################################
###### Scrpit will create Artikulate_tars folder in current directory#########  
##############################################################################

from git import Repo
import os
import tarfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
import glob
from datetime import datetime
import shutil
from lxml import etree

DESTINATION = "/tmp/artikulateCoursePackaging"
COURSES = "/tmp/artikulateCoursePackaging/courses"
DOWNLOAD_TARS = "upload"
SCRIPTS_DIR = "scripts"
SKELETONS ="/tmp/artikulateCoursePackaging/skeletons/"
HTML = "http://files.kde.org/edu/artikulate/"
PERCENTAGE = 0.1 # uncomment to create tars only for courses with more then 90 percent of the phrases 
# PERCENTAGE = 0 # uncomment to create tars for all the phrases regardless of number of recordings

# create a new directory for storing tars
if not os.path.exists(DOWNLOAD_TARS): os.makedirs(DOWNLOAD_TARS)

######  clone a repository to temp folder ###### 
repo = Repo.clone_from("git://anongit.kde.org/artikulate-data", DESTINATION)

######  setup reader access only ###### 
repo.config_reader()


##################################################################
###### create a tar file for each individual language course ###### 
##################################################################

# iterate through all skeletons
for skeleton in os.listdir(COURSES):
	
	# count phrases in skeleton
	skeleton_file = open(SKELETONS + skeleton + ".xml",'r')
	skelton_string = minidom.parseString(skeleton_file.read())
	skeleton_file.close()
	number_of_skeleton_phrases =len(skelton_string.getElementsByTagName('phrase'))
	
	# iterate through all languages for each skeleton
	for lang_course in os.listdir(COURSES + "/" + skeleton):
			
		# check number of recordings
		record_number = len(glob.glob1(COURSES + "/" + skeleton + "/" + lang_course ,"*.ogg"))
		
		if (record_number >=  PERCENTAGE * number_of_skeleton_phrases):
			# create tar file	
			tar_path = DOWNLOAD_TARS + "/"+ skeleton + "_" + lang_course + ".tar.bz2"
			tar = tarfile.open(tar_path, "w:bz2")
			tar.add(COURSES + "/" + skeleton + "/" + lang_course, arcname=lang_course)
			tar.close()

# function to change bytes into readable format
def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

#################################################################
#################### produce xml file ###########################
#################################################################
	
if os.listdir(DOWNLOAD_TARS)!=[] :	
	xml_file = open(DOWNLOAD_TARS + "/"+ "knewstuff.xml", "wb")
	html_file= open(DOWNLOAD_TARS + "/" + "artikulate_data.html", "wb")
	html_file.write("<table><thead><tr><th>Title</th><th>Language</th><th>Author(s)</th><th>Version</th></tr></thead><tbody>")
	root = ET.Element("knewstuff")

	for tar in os.listdir(DOWNLOAD_TARS):
		if tar.endswith(".tar.bz2"):

		 	# read xml file and fetch title/name and description/summary
			name_title = "unkown"
			summary = "unknown"
			language = "unknown"
			tar_file = tarfile.open(DOWNLOAD_TARS + "/" + tar)
			for name in tar_file.getnames():
				if name.endswith(".xml"):
					source_xml_file = etree.parse(tar_file.extractfile(tar_file.getmember(name)))

					nameElem = source_xml_file.find('title')
					name_title = nameElem.text

					summaryElem = source_xml_file.find('description')
					summary = summaryElem.text

					languageElem = source_xml_file.find('language')
					language = languageElem.text

			# get author's details from coresponding AUTHORS file
			author= "unknown"
			authors_mail="unknown"
			for name in tar_file.getnames():
				if "AUTHORS" in name:
					author_file = tar_file.extractfile(tar_file.getmember(name)).read().split()

					# parse author's name
					for i in range(1,len(author_file)-1):
						if author== "unknown":
							author = author_file[i]
						else:
							author = author + " "+ author_file[i]

					# parse author's mail
					authors_mail = author_file[len(author_file)-1][1:len(author_file[len(author_file)-1])-1]
			tar_file.close()    
	
			stuff = ET.SubElement(root, "stuff")

			# name
			field1 = ET.SubElement(stuff, "name")
			field1.text = name_title

			# type
			field2 = ET.SubElement(stuff, "type")
			field2.text = "artikulate/language"

			# author
			field3 = ET.SubElement(stuff, "author")
			field3.set("e-mail", authors_mail)
			field3.text = author

			# license
			# the spec has a typo and really uses "licence"
			field4 = ET.SubElement(stuff, "licence")
			field4.text =  "CC-BY-SA-3.0"

			# summary
			field4 = ET.SubElement(stuff, "summary")
			field4.set("lang", "en")
			field4.text = summary

			# version
			field5 = ET.SubElement(stuff, "version")
			field5.text = str(datetime.fromtimestamp(os.stat(DOWNLOAD_TARS + "/" + tar).st_mtime))[0:10]

			# release
			# must be an integer, increasing by every release
			field6 = ET.SubElement(stuff, "release")
			field6.text = "1"

			# releasedate
			field7 = ET.SubElement(stuff, "releasedate")
			field7.text = str(datetime.fromtimestamp(os.stat(DOWNLOAD_TARS + "/" + tar).st_mtime))[0:10] 

			# preview
			field8 = ET.SubElement(stuff, "preview")
			field8.set("lang", "en")
	
			# payload
			field9 = ET.SubElement(stuff, "payload")
			field9.set("lang", "en")
			field9.text = HTML + tar

			html_file.write("<tr>")
			html_file.write("<td><a href='" + tar + "'>" + name_title.encode('utf-8') + "</a></td>")
			html_file.write("<td>" + language.encode('utf-8') + "</td>")
			html_file.write("<td>" + author.encode('utf-8') + "</td>")
			html_file.write("<td>" + field7.text.encode('utf-8') + "</td>")
			html_file.write("</tr>")


	# save all to xml file	
	pretty_print_text = (minidom.parseString(ET.tostring(root)).toprettyxml(encoding='UTF-8'))
	doctype = '\n' + '<!DOCTYPE knewstuff SYSTEM "knewstuff.dtd">'+ '\n'
	xml_file.write(pretty_print_text.replace('\n', doctype, 1))
	xml_file.close()
	html_file.write("</tbody></table>");
	html_file.close()
	# move the page that includes the html_file, ready for uploading to edu.kde.org
	shutil.copyfile(SCRIPTS_DIR + "/artikulate.php", DOWNLOAD_TARS + "/artikulate.php")
	
	# remove DATA from tmp folder
	shutil.rmtree(DESTINATION)

