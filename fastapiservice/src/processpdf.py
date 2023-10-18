import requests
from pypdf import PdfReader
import io
import os
import re
import datetime
from dotenv import load_dotenv
load_dotenv()
from .utilities.customexception import CustomException

FILE_CACHE = os.getenv("FILE_CACHE")

class ProcessPDF:

    def __init__(self, inputPDFLink, *args) -> None:
        self.inputPDFLink = inputPDFLink.strip()
        self.downloadedPDFLocation = ""
        self.processedPDFLocation = ""
        if len(args) == 1:
            self.nougatAPIServerURL = args[0].strip()

    def getDownloadedPDFLocation(self):
        return self.downloadedPDFLocation
    
    def getProcessedPDFLocation(self):
        return self.processedPDFLocation
    
    def deleteFileFromFileCache(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted the file from FileCache: {filename}")

    def validatePDFLink(self):
        if self.inputPDFLink == "":
            return {"message":"No PDF Link Given", "details":{'status':400,'message': 'Please supply non-empty reference PDF link to finetune a model'}}
        try:
            response = requests.head(self.inputPDFLink)
            content_type = response.headers.get("Content-Type")
            if response.status_code==200 and ('application/pdf' in content_type.lower()):
                print(f"Validation PDF Link Successful : {self.inputPDFLink}")
                return {"message":"Validation PDF Link Successful", "details":{'status':200,'message': 'Successfully validated the PDF Link'}}
            else:
                print(f"Validation PDF Link Unsuccessful : {self.inputPDFLink}")
                return{"message":"Invalid PDF Link", "details":{'status':400,'referenceLink':self.inputPDFLink,'message': str(response.status_code) + ' ' + response.reason}} 
        except Exception as e:
            print(f"Validation PDF Link Unsuccessful : {self.inputPDFLink}")
            return{"message":"Invalid PDF Link", "details":{'referenceLink':self.inputPDFLink, 'error':str(e)}}
        
    def downloadPDF(self, fileid):

        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%m_%d_%Y_%H_%M_%S")
        pdf_filename =  "InputPDF_" + formatted_datetime + fileid +  ".pdf"

        try:
            response = requests.get(self.inputPDFLink)
            content_type = response.headers.get("Content-Type")
            if response.status_code==200 and ('application/pdf' in content_type.lower()):
                with open(FILE_CACHE + pdf_filename, 'wb') as file:
                    file.write(response.content)
                self.downloadedPDFLocation = pdf_filename
                print(f"Download PDF Successful : {self.downloadedPDFLocation}")
                return True
            else:
                print(f"Download PDF Unsuccessful : {self.downloadedPDFLocation}")
                return {"message":"Invalid PDF Link", "details":{'status':400,'referenceLink':self.inputPDFLink,'message': str(response.status_code) + ' ' + response.reason}}
        except Exception as e:
            print(f"Download PDF Unsuccessful : {self.downloadedPDFLocation}")
            return{"message":"Problem Accessing PDF Link", "details":{'referenceLink':self.inputPDFLink, 'error':str(e)}}

    def pyPDFProcessor(self, fileid):
        if self.downloadPDF(fileid):
            pdf_filename = FILE_CACHE + self.downloadedPDFLocation
            try:
                if self.downloadedPDFLocation !="":
                    reader = PdfReader(pdf_filename)
                    pages = reader.pages[:]
                    contents = "".join([page.extract_text() for page in pages])
                    mmd_filename = self.downloadedPDFLocation[:-3] + "mmd"
                    with open(FILE_CACHE + mmd_filename, 'w') as file:
                        file.write(contents)
                    self.processedPDFLocation = mmd_filename
                    return {"message":"PDF Processing Successful via PyPDF", "details":{'status':'201', 'message':"Successfully processed PDF using Nougat",'referenceLink':self.inputPDFLink}}
            except Exception as e:
                return {"message":"Problem Processing PDF via PyPDF", "details":{'referenceLink':self.inputPDFLink, 'error':str(e)}}
        
    def nougatProcesor(self, fileid):
        if self.downloadPDF(fileid):
            pdf_filename = FILE_CACHE + self.downloadedPDFLocation

            if self.downloadedPDFLocation !="":
                with open(pdf_filename, 'rb') as file:
                    pdfFile = file.read()
                nougatAPIHeaders = { "Accept":"application/json"}
                nougatAPIInputPDF = {'file':pdfFile}
                try:
                    print(f"Sending valid downloaded PDF to NougatAPIServerURL: {self.nougatAPIServerURL}")
                    response = requests.post(self.nougatAPIServerURL + "/predict", headers=nougatAPIHeaders, files=nougatAPIInputPDF)
                    if response.status_code == 200: 
                        cleanData = response.content[1:-1].decode().replace(r"\n\n",'\n\n').replace(r"\n",'\n').replace('\\\\', '\\')   
                        mmd_filename = self.downloadedPDFLocation[:-3] + "mmd"
                        with open(FILE_CACHE + mmd_filename, 'w') as file:
                            file.write(cleanData)
                        self.processedPDFLocation = mmd_filename
                        return {'message':"PDF Processing Successful via Nougat", "details":{'status':'201', 'message':"Successfully processed PDF using Nougat",'referenceLink':self.inputPDFLink}}
                    elif response.status_code == 404:
                        self.deleteFileFromFileCache(pdf_filename)
                        return {'message':"Connection Lost", "details":{'status':'404', 'message':"Check if Nougat API server is accessible via the Nougat API URL",'referenceLink':self.inputPDFLink}}
                        #raise(CustomException(message="Connection Lost", details={'status':'500', 'message':"Check if Nougat API server is accessible via the Nougat API URL",'referenceLink':self.inputPDFLink})) 
                    elif response.status_code == 422:
                        self.deleteFileFromFileCache(pdf_filename)
                        return {"message":"PDF Missing", "details":{'status':'422', 'message':"Please provide a PDF to Nougat API server",'referenceLink':self.inputPDFLink}}
                        #raise(CustomException(message="PDF Missing", details={'status':'400', 'message':"Please provide a PDF to Nougat API server",'referenceLink':self.inputPDFLink})) 
                    elif response.status_code == 502:
                        self.deleteFileFromFileCache(pdf_filename)
                        return {"message":"Nougat API Endpoint Issue", "details":{'status':'502', 'message':"Check if Nougat API server is running", 'referenceLink':self.inputPDFLink}}
                        #raise(CustomException(message="Nougat API Endpoint Issue", details={'status':'500', 'message':"Check if Nougat API server is running", 'referenceLink':self.inputPDFLink})) 
                except Exception as e:
                    self.deleteFileFromFileCache(pdf_filename)
                    return {"message":"Unknown Issue", "details":{'status':'500', 'message':"Connection to Nougat API Server lost! Check if the server is active or if the API URL is correct", 'referenceLink':self.inputPDFLink, 'error':str(e)}}
                    #raise(CustomException(message="Connection Lost", details={'status':'500', 'message':"Connection to Nougat API Server lost! Check if the server is active or if the API URL is correct", 'referenceLink':self.inputPDFLink, 'error':str(e)})) 
        
    def chunkPDF(self):
        pass
    
    def generateQuestions(self):
        pass
    
    def generateAnswers(self):
        pass
    
    def createTrainTestDataset(self):
        pass
    
    def fineTuneDataset(self):
        pass