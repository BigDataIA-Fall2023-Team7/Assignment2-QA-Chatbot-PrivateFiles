from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from .processpdf import ProcessPDF
import pandas as pd
from dotenv import load_dotenv
import os
import openai
import time

load_dotenv()
FILE_CACHE = os.getenv("FILE_CACHE")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
openai.api_key = os.getenv("OPENAI_API_KEY")

class CreateModelRequestPayload(BaseModel):
    referencePDFLinks: list
    nougatAPIServerURL: Optional[str] = None

class ChatQuestion(BaseModel):
    chatQuestion: str

app = FastAPI()

def get_embeddings(context):
    try:
        response = openai.Embedding.create(model=EMBEDDING_MODEL, input=context)
        return response["data"][0]["embedding"]
    except Exception as e:
        print(e)
        return ""

@app.get('/')
def info():
    return JSONResponse(content={'message':'ChatBot API is working'}, status_code=200)

@app.post('/v1/createFineTuneModel')
def createModel(requestBody: CreateModelRequestPayload):
    if len(requestBody.referencePDFLinks):

        """
        TODO: Run the process to create the model.
        """
        
        chunkFileArray = []
        if requestBody.nougatAPIServerURL:
            for id, pdflink in enumerate(requestBody.referencePDFLinks):
                fileid = '_File' + str(id)
                processPDF = ProcessPDF(pdflink, requestBody.nougatAPIServerURL)
                step1 = processPDF.validatePDFLink()
                if step1["message"] == "Validation PDF Link Successful":
                    step2 = processPDF.nougatProcesor(fileid)
                    if step2["message"]=="PDF Processing Successful via Nougat":
                        step3 = processPDF.chunkPDF()
                        if step3["message"]=="MMD Chunking Successful":
                            chunkFileArray.append([step3["details"]['chunkFileLocation'], step3["details"]['formname']])
                    elif step2["message"]=="Connection Lost":
                        return JSONResponse(content=step2, status_code=404)
                    elif step2["message"]=="PDF Missing":
                        return JSONResponse(content=step2, status_code=422)
                    elif step2["message"]=="Nougat API Endpoint Issue":
                        return JSONResponse(content=step2, status_code=502)
                    elif step2["message"]=="Unknown Issue":
                        return JSONResponse(content=step2, status_code=500)
                else:
                    return JSONResponse(content=step1, status_code=400)

        else:
            for id, pdflink in enumerate(requestBody.referencePDFLinks):
                fileid = '_File' + str(id)
                processPDF = ProcessPDF(pdflink)
                step1 = processPDF.validatePDFLink()
                if step1["message"] == "Validation PDF Link Successful":
                    step2 = processPDF.pyPDFProcessor(fileid)
                    if step2["message"] == "PDF Processing Successful via PyPDF":
                        pass
                    elif step2["message"]=="Problem Processing PDF via PyPDF":
                        return JSONResponse(content=step2, status_code=500)
                else:
                    return JSONResponse(content=step1, status_code=400)
        
        #Step4 combining chunk files
        combinedChunksDF = pd.DataFrame()
        for i in chunkFileArray:
            currentChunkFileDF = pd.read_csv(FILE_CACHE + i[0])
            currentChunkFileDF['FormName'] = i[1]
            combinedChunksDF = pd.concat([combinedChunksDF, currentChunkFileDF[["FormName", "Chunk", "TokenCount"]]], ignore_index=True)
        
        combinedChunksDF = combinedChunksDF.rename(columns={'Chunk':'context'})
        # combinedChunksDF.to_csv(f"{FILE_CACHE}CombinedChunksDF.csv", index=False, header=True)

        #Step5 generating embeddings for content
        count = 0
        combinedChunksDF['embeddings'] = None
        for i, row in combinedChunksDF.iterrows():
            combinedChunksDF.at[i, 'embeddings'] = get_embeddings(row.context)
            if count == 2:
                time.sleep(65)
                count=0
            else:
                count+=1
        
        combinedChunksDF.to_csv(f"{FILE_CACHE}CombinedChunksDF.csv", index=False, header=True)


        return JSONResponse(content={'detail':requestBody.model_dump(), 'message':'Created the fine tuned model for the given referencePDFLinks'}, status_code=201)
    else:
        raise HTTPException(status_code=400, detail={'message':'Inorder to create a fine-tuned chatbot model, please give links to PDF references'})
    

@app.post('/v1/getChatAnswer')
def chat(chatQuestion: ChatQuestion):
    if chatQuestion.chatQuestion:

        """
        TODO: Run the process to create the model.
        """

        # chatanswer = uddhavFunction(chatQuestion.chatQuestion, modelNameFromEnv, CONTEXT_DF_FILELOCATION)
                
        return JSONResponse(content={'chatQuestion': chatQuestion.chatQuestion, 'chatAnswer': 'This is your answer from fine-tuned chatbot model!'}, status_code=200)
    else:
        raise HTTPException(status_code=400, detail={'message':'Inorder to get answer from chatbot, please supply a question.'})