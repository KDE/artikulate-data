##############################################################################
###### Scrpit will create Artikulate_tars folder in current directory#########  
##############################################################################

from git import Repo
import os, time
import stat
import tarfile
import xml.etree.ElementTree as ET
import lxml.etree as etree
from xml.dom import minidom

DESTINATION = "/tmp/DATA"
COURSES = "/tmp/DATA/courses"
DOWNLOAD_TARS = "Artikulate_tars"
HTML = "http://files.kde.org/edu/artikulate/"

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
	# iterate through all languages for each skeleton
	for lang_course in os.listdir(COURSES + "/" + skeleton):	
		### check if there are any recordings ???	
		tar_path = DOWNLOAD_TARS + "/"+ skeleton + "_" + lang_course + ".tar"
		tar = tarfile.open(tar_path, "w")
		tar.add(COURSES + "/" + skeleton + "/" + lang_course, arcname=lang_course)
		tar.close()

# function to change bytes into redable format
def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

#################################################################
#################### produce xml file ###########################
#################################################################
xml_file = open(DOWNLOAD_TARS + "/"+ "artikulate.xml", "wb")
root = ET.Element("knewstuff")


for tar in os.listdir(DOWNLOAD_TARS):
	stuff = ET.SubElement(root, "stuff")

	# name
	field1 = ET.SubElement(stuff, "name")
	field1.text = tar

	# type
	field2 = ET.SubElement(stuff, "type")
	field2.text = "artikulate/language"

	# author
	field3 = ET.SubElement(stuff, "author")
	field3.set("e-mail", "konkiewicz.m@gmail.com")
	field3.text = "Magda Konkiewicz"

	# licence
	field4 = ET.SubElement(stuff, "licence")
	field4.text = "GPL"

	# summary
	field4 = ET.SubElement(stuff, "summary")
	field4.set("lang", "en")
	field4.text = tar + " - " + sizeof_fmt((os.path.getsize(DOWNLOAD_TARS + "/" + tar)))

	# version
	field5 = ET.SubElement(stuff, "version")
	field5.text = "1.0"

	# release
	field6 = ET.SubElement(stuff, "release")
	field6.text = "1"

	# releasedate
	field7 = ET.SubElement(stuff, "releasedate")
	field7.text = time.ctime(os.path.getmtime(DOWNLOAD_TARS + "/" + tar))

	# preview
	field8 = ET.SubElement(stuff, "preview")
	field8.set("lang", "en")
	
	# payload
	field9 = ET.SubElement(stuff, "payload")
	field9.set("lang", "en")
	field9.text = HTML + tar

	# rating
	field10 = ET.SubElement(stuff, "rating")
	field10.text = "5"
	
	# downloads
	field11 = ET.SubElement(stuff, "downloads")
	field11.text = "0"

# save all to xml file	
pretty_print_text = (minidom.parseString(ET.tostring(root)).toprettyxml(encoding='UTF-8'))
doctype = '\n' + '<!DOCTYPE knewstuff SYSTEM "knewstuff.dtd">'+ '\n'
xml_file.write(pretty_print_text.replace('\n', doctype, 1))






