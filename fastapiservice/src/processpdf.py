import requests
from pypdf import PdfReader
import re
import io
import os
import re
import datetime
import tiktoken
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from .utilities.customexception import CustomException

FILE_CACHE = os.getenv("FILE_CACHE")
TOKEN_LIMIT = int(os.getenv("TOKEN_LIMIT"))
GPT_MODEL = os.getenv("GPT_MODEL")

class ProcessPDF:

    def __init__(self, inputPDFLink, *args) -> None:
        self.inputPDFLink = inputPDFLink.strip()
        self.downloadedPDFLocation = ""
        self.processedPDFLocation = ""
        self.pdfname = ""
        self.chunkFileLocation = ""
        if len(args) == 1:
            self.nougatAPIServerURL = args[0].strip()

    def num_tokens(self,text: str, model: str = GPT_MODEL) -> int:
        """Return the number of tokens in a string."""
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    
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
        # pdf_filename =  "InputPDF_" + formatted_datetime + fileid +  ".pdf"

        match = re.search(r'\/([^/]+\.pdf)$', self.inputPDFLink)
        if match:
            pdf_filename =  match.group(1)
        else:
            pdf_filename =  "InputPDF_" + fileid +  ".pdf"

        self.pdfname = pdf_filename


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
                    print("PyPDF Processing Done")
                    return {"message":"PDF Processing Successful via PyPDF", "details":{'status':'201', 'message':"Successfully processed PDF using PyPDF",'referenceLink':self.inputPDFLink}}
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
                        print("Nougat Processing Done")
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

        print("Chunking MMD")
        semantics_df_rows = []
        semantics_df_headers = ["FormName", "ParaNumber", "ParaContent", "ParaCharacterCount", "ParaSemantics", "Section", "TokenCount", "CummulativeTokenCount"]
            
        mmdFileLocation = FILE_CACHE + self.processedPDFLocation
        with open(mmdFileLocation, 'r') as file:
            mmdFileContents = file.read()

        print('Cleaning MMD Contents')

        #Cleaning Tables and Warnings in MMD File

        #Cleaning Tables
        pattern = r'\\begin{tabular}.*?\n'
        print(f"Tables Identified : {len(re.findall(pattern, mmdFileContents))}")
        mmdFileContents = re.sub(pattern, '\n',mmdFileContents)

        pattern = r'\\end{tabular}.*?\n'
        mmdFileContents = re.sub(pattern, '\n',mmdFileContents)

        pattern = r'\\begin{table}.*?\n'
        print(f"Tables Identified : {len(re.findall(pattern, mmdFileContents))}")
        mmdFileContents = re.sub(pattern, '\n',mmdFileContents)

        pattern = r'\\end{table}.*?\n'
        mmdFileContents = re.sub(pattern, '\n',mmdFileContents)

        #Cleaning Warnings
        pattern = r'\+\+\+(.*?)\+\+\+'
        print(f"Warnings Identified : {len(re.findall(pattern, mmdFileContents, re.DOTALL))}")
        mmdFileContents = re.sub(pattern, '\n',mmdFileContents,flags=re.DOTALL)

        listOfParagraphs = mmdFileContents.split("\n")

        listOfParagraphsAfterCleaning = []
        cummulativetokencount = 0
        with open(f'{mmdFileLocation}.log', 'w') as f:
            for i, paragraph in enumerate(listOfParagraphs):
                if len(paragraph)!=0:
                    listOfParagraphsAfterCleaning.append(paragraph)

                    #TokenCount for each row in semantics_df
                    tokencount = self.num_tokens(paragraph, GPT_MODEL)
                    cummulativetokencount+=tokencount

                    #Compute ParaSemantics in semantics_df
                    #["FormName", "ParaNumber", "ParaContent", "ParaCharacterCount", "ParaSemantics"]
                    
                    if paragraph.startswith("###"):
                        parasemantics = "Heading3"
                    elif paragraph.startswith("##"):
                        parasemantics = "Heading2"
                    elif paragraph.startswith("#"):
                        parasemantics = "Heading1"
                    elif paragraph.startswith("**"):
                        parasemantics = "Bold"
                    elif paragraph.startswith("*"):
                        parasemantics = "Bullet"
                    else:
                        parasemantics = "Paragraph"
                    semantics_df_rows.append([self.processedPDFLocation[:-4], i, paragraph, len(paragraph), parasemantics, None, tokencount, cummulativetokencount])


                    f.write(f"P{str(i)} : {len(paragraph)}\n{paragraph}\n\n@@@\n\n")

        semantics_df = pd.DataFrame(data=semantics_df_rows, columns=semantics_df_headers)

        currentsectionnumber = 0
        firstheading = False

        for index, row in semantics_df.iterrows():
            if (row['ParaSemantics'] not in ["Heading3", "Heading2", "Heading1"]) and (firstheading!=True):
                currentsectionnumber+=1
                semantics_df.iloc[index, semantics_df.columns.get_loc('Section')] = currentsectionnumber
            elif (firstheading==True) and (row['ParaSemantics'] not in ["Heading3", "Heading2", "Heading1"]):
                 semantics_df.iloc[index, semantics_df.columns.get_loc('Section')] = currentsectionnumber
            else:
                firstheading = True
                currentsectionnumber+=1
                semantics_df.iloc[index, semantics_df.columns.get_loc('Section')] = currentsectionnumber

        semantics_df.to_csv(FILE_CACHE + f"{self.pdfname[:-4]}_semantics_df.csv", index=False, header=True)
        print("Generated Semantics File in FILE_CACHE")

        section_df = semantics_df.groupby('Section')['ParaContent'].agg('\n'.join).reset_index()
        section_df.rename(columns={'ParaContent': 'Chunk'}, inplace=True)
        section_df['TokenCount'] = section_df['Chunk'].apply(self.num_tokens, args=(GPT_MODEL,))
        section_df['CummulativeTokenCount'] = section_df['TokenCount'].cumsum()
        section_df.to_csv(FILE_CACHE + f"{self.pdfname[:-4]}_sections_df.csv", index=False, header=True)

        chunk_df_rows = []
        chunk_df_headers = ["Chunk", "TokenCount", "CummulativeTokenCount"]
        oversized_sections = []

        current_chunk_buffer = ""
        current_chunk_buffer_tokens=0
        for i, row in section_df.iterrows():
            if row['TokenCount'] > TOKEN_LIMIT:
                oversized_sections.append(row['Chunk'])
                if current_chunk_buffer!="":
                    chunk_df_rows.append([current_chunk_buffer, None, None])
                    current_chunk_buffer=""

            elif row['TokenCount'] + current_chunk_buffer_tokens < TOKEN_LIMIT:
                current_chunk_buffer = current_chunk_buffer + "\n" + row['Chunk']
            else:
                chunk_df_rows.append([current_chunk_buffer, None, None])
                current_chunk_buffer = row['Chunk']
            current_chunk_buffer_tokens = self.num_tokens(current_chunk_buffer,GPT_MODEL)
            
        if current_chunk_buffer!="":
            chunk_df_rows.append([current_chunk_buffer, None, None])

        chunk_df = pd.DataFrame(data=chunk_df_rows, columns=chunk_df_headers)
        chunk_df['TokenCount']=chunk_df["Chunk"].apply(self.num_tokens, args=(GPT_MODEL,))

        print("Generated Initial Chunk File in FILE_CACHE")

        if len(oversized_sections)!=0:
            for oversized_section in oversized_sections:
                common_shared_heading = ""
                oversizedDf_headers = ["Sentence", "TokenCount", "CummulativeTokenCount"]
                pattern = r'(.*?)\n'
                sentences = re.split(pattern, oversized_section)
                oversizedDf_rows = [[s.strip(), self.num_tokens(s.strip(), GPT_MODEL), None] for s in sentences if s.strip()]
                oversizedDf = pd.DataFrame(data=oversizedDf_rows, columns=oversizedDf_headers)
                if oversizedDf.iloc[0]['Sentence'].startswith('#'):
                    common_shared_heading = oversizedDf.iloc[0]['Sentence']
                    oversizedDf = oversizedDf.drop(0)

                oversizedDf_rows = []
                current_chunk_buffer = common_shared_heading
                current_chunk_buffer_tokens=0
                for i, row in oversizedDf.iterrows():
                    if row['TokenCount'] + current_chunk_buffer_tokens < TOKEN_LIMIT:
                        current_chunk_buffer = current_chunk_buffer + '\n' + row["Sentence"]
                    else:
                        oversizedDf_rows.append([current_chunk_buffer, None, None])
                        current_chunk_buffer = common_shared_heading + row['Sentence']

                    current_chunk_buffer_tokens = self.num_tokens(current_chunk_buffer,GPT_MODEL)

                if current_chunk_buffer!="":
                    oversizedDf_rows.append([current_chunk_buffer, None, None])
                
                tempDf = pd.DataFrame(data=oversizedDf_rows, columns=["Chunk", "TokenCount", "CummulativeTokenCount"])
                tempDf['TokenCount'] = tempDf['Chunk'].apply(self.num_tokens, args=(GPT_MODEL,))
                chunk_df = pd.concat([chunk_df, tempDf], ignore_index=True)
                print("Updated Chunk File for oversized sections in FILE_CACHE")


        chunk_df['CummulativeTokenCount']=chunk_df["TokenCount"].cumsum()
        chunk_df.to_csv(FILE_CACHE + f"{self.pdfname[:-4]}_chunks_df.csv", index=False, header=True)
        self.chunkFileLocation = f"{self.pdfname[:-4]}_chunks_df.csv"
        print("Chunking Complete")
        return {'message':"MMD Chunking Successful", "details":{'status':'201', 'message':"Successfully chunked processed mmd",'referenceLink':self.inputPDFLink, 'chunkFileLocation':self.chunkFileLocation, 'formname':self.pdfname[:-4]}}

    
    def generateQuestions(self):
        pass
    
    def generateAnswers(self):
        pass
    
    def createTrainTestDataset(self):
        pass
    
    def fineTuneDataset(self):
        pass