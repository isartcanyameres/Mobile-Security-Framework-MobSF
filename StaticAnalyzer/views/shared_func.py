# -*- coding: utf_8 -*-
"""
Module providing the shared functions for static analysis of iOS and Android
"""
import os, hashlib, io, re, zipfile, subprocess, platform

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.template.defaulttags import register

from MobSF.utils import PrintException
from MobSF.utils import python_list
from MobSF.utils import python_dict

from StaticAnalyzer.models import StaticAnalyzerAndroid
from StaticAnalyzer.models import StaticAnalyzerIPA
from StaticAnalyzer.models import StaticAnalyzerIOSZIP

try:
    import StringIO
    StringIO = StringIO.StringIO
except Exception:
    from io import StringIO

try:
    import xhtml2pdf.pisa as pisa
except:
    PrintException("[ERROR] xhtml2pdf is not installed. Cannot generate PDF reports")

def FileSize(APP_PATH):
    """Return the size of the file."""
    return round(float(os.path.getsize(APP_PATH)) / (1024 * 1024),2)

def HashGen(APP_PATH):
    """Generate and return sha1 and sha256 as a tupel."""
    try:
        print "[INFO] Generating Hashes"
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        BLOCKSIZE = 65536
        with io.open(APP_PATH, mode='rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while buf:
                sha1.update(buf)
                sha256.update(buf)
                buf = afile.read(BLOCKSIZE)
        sha1val = sha1.hexdigest()
        sha256val=sha256.hexdigest()
        return sha1val, sha256val
    except:
        PrintException("[ERROR] Generating Hashes")

def Unzip(APP_PATH, EXT_PATH):
    print "[INFO] Unzipping"
    try:
        files=[]
        with zipfile.ZipFile(APP_PATH, "r") as z:
                z.extractall(EXT_PATH)
                files=z.namelist()
        return files
    except:
        PrintException("[ERROR] Unzipping Error")
        if platform.system()=="Windows":
            print "\n[INFO] Not yet Implemented."
        else:
            print "\n[INFO] Using the Default OS Unzip Utility."
            try:
                subprocess.call(['unzip', '-o', '-q', APP_PATH, '-d', EXT_PATH])
                dat=subprocess.check_output(['unzip','-qq','-l',APP_PATH])
                dat=dat.split('\n')
                x=['Length   Date   Time   Name']
                x=x+dat
                return x
            except:
                PrintException("[ERROR] Unzipping Error")

def PDF(request):
    try:
        MD5=request.GET['md5']
        TYP=request.GET['type']
        m=re.match('^[0-9a-f]{32}$',MD5)
        if m:
            if TYP in ['APK','ANDZIP']:
                DB=StaticAnalyzerAndroid.objects.filter(MD5=MD5)
                if DB.exists():
                    print "\n[INFO] Fetching data from DB for PDF Report Generation (Android)"
                    context = {
                    'title' : DB[0].TITLE,
                    'name' : DB[0].APP_NAME,
                    'size' : DB[0].SIZE,
                    'md5': DB[0].MD5,
                    'sha1' : DB[0].SHA1,
                    'sha256' : DB[0].SHA256,
                    'packagename' : DB[0].PACKAGENAME,
                    'mainactivity' : DB[0].MAINACTIVITY,
                    'targetsdk' : DB[0].TARGET_SDK,
                    'maxsdk' : DB[0].MAX_SDK,
                    'minsdk' : DB[0].MIN_SDK,
                    'androvername' : DB[0].ANDROVERNAME,
                    'androver': DB[0].ANDROVER,
                    'manifest': DB[0].MANIFEST_ANAL,
                    'permissions' : DB[0].PERMISSIONS,
# Esteve 21.08.2016 - begin - Permission Analysis with Androguard
                    'androperms' : DB[0].ANDROPERMS,
# Esteve 21.08.2016 - end - Permission Analysis with Androguard
                    'files' : python_list(DB[0].FILES),
                    'certz' : DB[0].CERTZ,
                    'activities' : python_list(DB[0].ACTIVITIES),
                    'receivers' : python_list(DB[0].RECEIVERS),
                    'providers' : python_list(DB[0].PROVIDERS),
                    'services' : python_list(DB[0].SERVICES),
                    'libraries' : python_list(DB[0].LIBRARIES),
                    'act_count' : DB[0].CNT_ACT,
                    'prov_count' : DB[0].CNT_PRO,
                    'serv_count' : DB[0].CNT_SER,
                    'bro_count' : DB[0].CNT_BRO,
                    'certinfo': DB[0].CERT_INFO,
                    'issued':DB[0].ISSUED,
                    'native' : DB[0].NATIVE,
                    'dynamic' : DB[0].DYNAMIC,
                    'reflection' : DB[0].REFLECT,
                    'crypto': DB[0].CRYPTO,
                    'obfus': DB[0].OBFUS,
                    'api': DB[0].API,
                    'dang': DB[0].DANG,
                    'urls': DB[0].URLS,
                    'domains': python_dict(DB[0].DOMAINS),
                    'emails': DB[0].EMAILS,
                    'strings': python_list(DB[0].STRINGS),
# Esteve 14.08.2016 - begin - Pirated and Malicious App Detection with APKiD 
                    'apkid': DB[0].APKID,
# Esteve 14.08.2016 - end - Pirated and Malicious App Detection with APKiD 
                    'zipped' : DB[0].ZIPPED,
                    'mani': DB[0].MANI
                    }
                    if TYP=='APK':
                        template= get_template("static_analysis_pdf.html")
                    else:
                        template= get_template("static_analysis_zip_pdf.html")
            elif re.findall('IPA|IOSZIP',TYP):
                if TYP=='IPA':
                    DB=StaticAnalyzerIPA.objects.filter(MD5=MD5)
                    if DB.exists():
                        print "\n[INFO] Fetching data from DB for PDF Report Generation (IOS IPA)"
                        context = {
                        'title' : DB[0].TITLE,
                        'name' : DB[0].APPNAMEX,
                        'size' : DB[0].SIZE,
                        'md5': DB[0].MD5,
                        'sha1' : DB[0].SHA1,
                        'sha256' : DB[0].SHA256,
                        'plist' : DB[0].INFOPLIST,
                        'bin_name' : DB[0].BINNAME,
                        'id' : DB[0].IDF,
                        'ver' : DB[0].VERSION,
                        'sdk' : DB[0].SDK,
                        'pltfm' : DB[0].PLTFM,
                        'min' : DB[0].MINX,
                        'bin_anal' : DB[0].BIN_ANAL,
                        'libs' : DB[0].LIBS,
                        'files' : python_list(DB[0].FILES),
                        'file_analysis' : DB[0].SFILESX,
                        'strings' : DB[0].STRINGS
                        }
                        template= get_template("ios_binary_analysis_pdf.html")
                elif TYP=='IOSZIP':
                    DB=StaticAnalyzerIOSZIP.objects.filter(MD5=MD5)
                    if DB.exists():
                        print "\n[INFO] Fetching data from DB for PDF Report Generation (IOS ZIP)"
                        context = {
                        'title' : DB[0].TITLE,
                        'name' : DB[0].APPNAMEX,
                        'size' : DB[0].SIZE,
                        'md5': DB[0].MD5,
                        'sha1' : DB[0].SHA1,
                        'sha256' : DB[0].SHA256,
                        'plist' : DB[0].INFOPLIST,
                        'bin_name' : DB[0].BINNAME,
                        'id' : DB[0].IDF,
                        'ver' : DB[0].VERSION,
                        'sdk' : DB[0].SDK,
                        'pltfm' : DB[0].PLTFM,
                        'min' : DB[0].MINX,
                        'bin_anal' : DB[0].BIN_ANAL,
                        'libs' : DB[0].LIBS,
                        'files' : python_list(DB[0].FILES),
                        'file_analysis' : DB[0].SFILESX,
                        'api' : DB[0].HTML,
                        'insecure' : DB[0].CODEANAL,
                        'urls' : DB[0].URLnFile,
                        'domains': python_dict(DB[0].DOMAINS),
                        'emails' : DB[0].EmailnFile
                        }
                        template= get_template("ios_source_analysis_pdf.html")
            else:
                return HttpResponseRedirect('/error/')
            html  = template.render(context)
            result = StringIO()
            pdf = pisa.pisaDocument(StringIO( "{0}".format(html.encode('utf-8'))), result, encoding='utf-8')
            if not pdf.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
            else:
                return HttpResponseRedirect('/error/')
        else:
            return HttpResponseRedirect('/error/')
    except:

        PrintException("[ERROR] PDF Report Generation Error")
        return HttpResponseRedirect('/error/')
