from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from .processpdf import ProcessPDF

class CreateModelRequestPayload(BaseModel):
    referencePDFLinks: list
    nougatAPIServerURL: Optional[str] = None

class ChatQuestion(BaseModel):
    chatQuestion: str

app = FastAPI()

@app.get('/')
def info():
    return JSONResponse(content={'message':'ChatBot API is working'}, status_code=200)

@app.post('/v1/createFineTuneModel')
def createModel(requestBody: CreateModelRequestPayload):
    if len(requestBody.referencePDFLinks):

        """
        TODO: Run the process to create the model.
        """
        

        if requestBody.nougatAPIServerURL:
            for id, pdflink in enumerate(requestBody.referencePDFLinks):
                fileid = '_File' + str(id)
                processPDF = ProcessPDF(pdflink, requestBody.nougatAPIServerURL)
                step1 = processPDF.validatePDFLink()
                if step1["message"] == "Validation PDF Link Successful":
                    step2 = processPDF.nougatProcesor(fileid)
                    if step2["message"]=="PDF Processing Successful via Nougat":
                        pass
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
        
        return JSONResponse(content={'detail':requestBody.model_dump(), 'message':'Created the fine tuned model for the given referencePDFLinks'}, status_code=201)
    else:
        raise HTTPException(status_code=400, detail={'message':'Inorder to create a fine-tuned chatbot model, please give links to PDF references'})
    

@app.post('/v1/getChatAnswer')
def chat(chatQuestion: ChatQuestion):
    if chatQuestion.chatQuestion:

        """
        TODO: Run the process to create the model.
        """
                
        return JSONResponse(content={'chatQuestion': chatQuestion.chatQuestion, 'chatAnswer': 'This is your answer from fine-tuned chatbot model!'}, status_code=200)
    else:
        raise HTTPException(status_code=400, detail={'message':'Inorder to get answer from chatbot, please supply a question.'})